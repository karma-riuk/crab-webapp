import fs from "fs";
import { getProjectPath } from "../utils/paths.js";
import { bleu } from "../utils/bleu.js";

function buildReferenceMap(dataset_path) {
    const referenceMap = {};
    const dataset = JSON.parse(fs.readFileSync(dataset_path));
    for (const entry of dataset.entries) {
        const id = entry.metadata.id;
        const comments = entry.comments;
        referenceMap[id] = comments.map((c) => c.body);
    }
    return referenceMap;
}

const REFERENCE_MAP = buildReferenceMap(getProjectPath("data/dataset.json"));

export const evaluate_comments = (answers, percent_cb) => {
    const total = Object.keys(answers).length;
    let i = 0;
    const results = {};
    for (const [id, generated_comment] of Object.entries(answers)) {
        const n_tokens_generated = generated_comment.trim().split(/\s+/).length;
        if (!(id in REFERENCE_MAP)) {
            console.error(`id: "${id}" is not present in the dataset`);
            continue;
        }
        const paraphrases = REFERENCE_MAP[id];

        let maxScore = 0;
        const scores = [];
        for (const paraphrase of paraphrases) {
            const n_tokens_paraphrase = paraphrase.trim().split(/\s+/).length;
            const max_n = Math.min(n_tokens_generated, n_tokens_paraphrase, 4);
            const score = bleu(paraphrase, generated_comment, max_n);
            scores.push(score);
            maxScore = Math.max(score, maxScore);
        }
        results[id] = {
            max_bleu_score: maxScore,
            bleu_scores: scores,
            proposed_comment: generated_comment,
        };
        percent_cb(Math.floor((++i / total) * 100));
    }
    return results;
};

export const evaluate_refinement = (answers, percent_cb) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        // await new Promise((res) => setTimeout(res, 1000));
        console.log("Done");
        percent_cb(Math.floor((++i / total) * 100));
    }
};
