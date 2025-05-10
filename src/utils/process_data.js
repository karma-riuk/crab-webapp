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
        // console.log(`Processing ${i} ${id}...`);
        if (!(id in REFERENCE_MAP)) {
            // throw new Error(`id: "${id}" is not present in the dataset`);
            console.error(`id: "${id}" is not present in the dataset`);
            continue;
        }
        const paraphrases = REFERENCE_MAP[id];

        let maxScore = 0;
        const scores = [];
        for (const paraphrase of paraphrases) {
            const score = bleu(paraphrase, generated_comment, 4); // TODO: ask prof what number show be here
            scores.push(score);
            maxScore = Math.max(score, maxScore);
        }
        results[id] = {
            "max bleu score": maxScore,
            "bleu scores": scores,
            "proposed comment": generated_comment,
        };
        percent_cb(Math.floor((++i / total) * 100));
    }
    return results;
};

export const evaluate_refinement = async (answers, percent_cb, finished_cb) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        await new Promise((res) => setTimeout(res, 1000));
        console.log("Done");
        percent_cb(Math.floor((++i / total) * 100));
    }
};
