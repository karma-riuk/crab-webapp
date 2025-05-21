from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json, uuid

from utils.errors import InvalidJsonFormatError

# fmt: off
@dataclass
class FileData:
    is_code_related: bool
    coverage: Dict[str, float] # jacoco-report -> coverage
    content_before_pr: str = ""
    content_after_pr: str = ""

@dataclass
class Comment:
    body: str
    file: str
    from_: int
    to: int
    paraphrases: List[str] = field(default_factory=list)

@dataclass
class Selection:
    comment_suggests_change: bool
    diff_after_address_change: Optional[bool]
    is_code_related: bool

class ArchiveState(Enum):
    BASE = "base"
    MERGED = "merged"

@dataclass
class Metadata:
    id: str
    repo: str   # the name of the repo, with style XXX/YYY
    pr_number: int
    pr_title: str
    pr_body: str
    merge_commit_sha: str   # to checkout for the tests
    successful: bool = True
    build_system: str = ""
    reason_for_failure: str = ""
    last_cmd_error_msg: str = ""
    selection: Optional[Selection] = None

    def archive_name(self, state: ArchiveState, only_id:bool=False):
        if only_id:
            return f"{self.id}_{state.value}.tar.gz"
        return f"{self.repo.replace('/', '_')}_{self.pr_number}_{state.value}.tar.gz"

@dataclass
class CommentGenSubmission:
    path: str
    line_from: int
    line_to: Optional[int]
    body: str

    @classmethod
    def json_parse(cls, data) -> "CommentGenSubmission":
        if not isinstance(data, dict):
            raise InvalidJsonFormatError("Submitted json doesn't contain an object")
        if not all(k in data and isinstance(data[k], str) for k in ["path", "body"]):
            raise InvalidJsonFormatError("Submitted json doesn't contain the required fields")
        if not all(k in data and isinstance(data[k], (int, type(None))) for k in ["line_from", "line_to"]):
            raise InvalidJsonFormatError("Submitted json doesn't contain the required fields")

        return cls(
            path=data["path"],
            line_from=data["line_from"],
            line_to=data.get("line_to"),
            body=data["body"],
        )

@dataclass
class DatasetEntry:
    metadata: Metadata
    files: Dict[str, FileData]   # filename -> file data, files before the PR (before the first PR commits)
    diffs_before: Dict[str, str]   # filename -> diff, diffs between the opening of the PR and the comment
    comments: List[Comment]
    diffs_after: Dict[str, str]   # filename -> diff, changes after the comment


@dataclass
class CommentGenEntry:
    id: str
    files: Dict[str, str]   # filename -> file content
    diffs: Dict[str, str]   # filename -> diff, diffs between the opening of the PR and the comment

    @staticmethod
    def from_entry(entry: DatasetEntry) -> "CommentGenEntry":
        return CommentGenEntry(
            id=entry.metadata.id,
            files={fname: fdata.content_before_pr for fname, fdata in entry.files.items()},
            diffs=entry.diffs_before,
        )


@dataclass
class CodeRefinementEntry:
    id: str
    files: Dict[str, str]   # filename -> file content
    diffs: Dict[str, str]   # filename -> diff, diffs between the opening of the PR and the comment
    comments: List[Comment]

    @staticmethod
    def from_entry(entry: DatasetEntry) -> "CodeRefinementEntry":
        return CodeRefinementEntry(
            id=entry.metadata.id,
            files={fname: fdata.content_before_pr for fname, fdata in entry.files.items()},
            diffs=entry.diffs_before,
            comments=entry.comments,
        )

class OutputType(Enum):
    FULL = "full"
    CODE_REFINEMENT = "code_refinement"
    COMMENT_GEN = "comment_gen"

# fmt: on
@dataclass
class Dataset:
    entries: List[DatasetEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return sum(1 for entry in self.entries if entry.metadata.successful)

    def to_json(
        self,
        filename: str,
        type_: OutputType = OutputType.FULL,
        remove_non_suggesting: bool = False,
    ) -> None:
        """Serialize the dataset to a JSON file"""

        entries_to_dump = self.entries

        if type_ == OutputType.COMMENT_GEN:
            entries_to_dump = [
                entry
                for entry in self.entries
                if entry.metadata.selection and entry.metadata.selection.comment_suggests_change
            ]
        elif type_ == OutputType.CODE_REFINEMENT:
            entries_to_dump = [
                entry
                for entry in self.entries
                if entry.metadata.selection
                and entry.metadata.selection.diff_after_address_change
                and entry.metadata.selection.is_code_related
            ]
        elif type_ == OutputType.FULL and remove_non_suggesting:
            entries_to_dump = [
                entry
                for entry in self.entries
                if entry.metadata.selection and entry.metadata.selection.comment_suggests_change
            ]

        to_dump = Dataset(entries=entries_to_dump)
        # print(f"{len(entries_to_dump)} entries...", end=" ", flush=True)

        def transform_entry(entry: Union[DatasetEntry, Dataset, Any]) -> Union[dict, list]:
            if not isinstance(entry, (DatasetEntry, Dataset)):
                return entry.__dict__

            if type_ == OutputType.FULL:
                return entry.__dict__

            if isinstance(entry, Dataset):
                return entry.entries

            if type_ == OutputType.COMMENT_GEN:
                return CommentGenEntry.from_entry(entry).__dict__

            if type_ == OutputType.CODE_REFINEMENT:
                return CodeRefinementEntry.from_entry(entry).__dict__

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(to_dump, f, default=transform_entry, indent=4)

    @staticmethod
    def from_json(filename: str, keep_still_in_progress: bool = False) -> "Dataset":
        with open(filename, "r", encoding="utf-8") as f:
            print(f"Loading dataset from {filename}...", end=" ", flush=True)
            data = json.load(f)
            print("Done")

        entries = []
        for entry_data in data["entries"]:
            metadata_data = entry_data["metadata"]
            selection_data = metadata_data["selection"] if "selection" in metadata_data else None
            selection = Selection(**selection_data) if selection_data else None
            metadata_data["selection"] = selection
            if "id" not in metadata_data:
                metadata_data["id"] = uuid.uuid4().hex
            metadata = Metadata(**metadata_data)

            if (
                not keep_still_in_progress
                and metadata.reason_for_failure == "Was still being processed"
            ):
                continue

            files = {fname: FileData(**fdata) for fname, fdata in entry_data["files"].items()}

            comments = [Comment(**comment) for comment in entry_data["comments"]]

            entry = DatasetEntry(
                metadata=metadata,
                files=files,
                diffs_before=entry_data["diffs_before"],
                comments=comments,
                diffs_after=entry_data["diffs_after"],
            )
            entries.append(entry)

        return Dataset(entries=entries)

    def build_reference_map(self) -> Dict[str, DatasetEntry]:
        """Build a reference map for the dataset"""

        ref_map = {}
        for entry in self.entries:
            ref_map[entry.metadata.id] = entry
        return ref_map
