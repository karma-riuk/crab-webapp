from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json, uuid

from utils.errors import InvalidJsonFormatError


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
    is_covered: Optional[bool] = None
    is_code_related: Optional[bool] = None
    successful: Optional[bool] = None
    build_system: str = ""
    reason_for_failure: str = ""
    last_cmd_error_msg: str = ""
    selection: Optional[Selection] = None

    def archive_name(self, state: ArchiveState, only_id: bool = False):
        if only_id:
            return f"{self.id}_{state.value}.tar.gz"
        return f"{self.repo.replace('/', '_')}_{self.pr_number}_{state.value}.tar.gz"


@dataclass
class CommentGenSubmission:
    path: str
    from_: Optional[int]
    to: int
    body: str

    @classmethod
    def json_parse(cls, data) -> "CommentGenSubmission":
        if not isinstance(data, dict):
            raise InvalidJsonFormatError("Submitted json doesn't contain an object")
        if not all(k in data and isinstance(data[k], str) for k in ["path", "body"]):
            raise InvalidJsonFormatError("Submitted json doesn't contain the required fields")
        if not all(k in data and isinstance(data[k], (int, type(None))) for k in ["from_", "to"]):
            raise InvalidJsonFormatError("Submitted json doesn't contain the required fields")

        return cls(
            path=data["path"],
            from_=data.get("from_"),
            to=data["to"],
            body=data["body"],
        )


@dataclass
class DatasetEntry:
    metadata: Metadata
    comments: List[Comment]


class OutputType(Enum):
    FULL = "full"
    CODE_REFINEMENT = "code_refinement"
    COMMENT_GEN = "comment_gen"


@dataclass
class Dataset:
    entries: List[DatasetEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return sum(1 for entry in self.entries if entry.metadata.successful)

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

            comments = [Comment(**comment) for comment in entry_data["comments"]]

            entry = DatasetEntry(
                metadata=metadata,
                comments=comments,
            )
            entries.append(entry)

        return Dataset(entries=entries)

    def build_reference_map(self) -> Dict[str, DatasetEntry]:
        """Build a reference map for the dataset"""

        ref_map = {}
        for entry in self.entries:
            ref_map[entry.metadata.id] = entry
        return ref_map
