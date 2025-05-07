import fs from "fs";
import { getProjectPath } from "../utils/paths.js";
import { bleu } from "bleu-score";

const DATASET_PATH = getProjectPath("data/dataset.json");

export const evaluate_comments = async (answers, percent_cb) => {
    console.log(`Reading dataset...`);
    const raw = fs.readFileSync(DATASET_PATH);
    const dataset = JSON.parse(raw);

    console.log(`Building reference map...`);
    const referenceMap = {};
    for (const entry of dataset.entries) {
        const id = entry.metadata.id;
        const comments = entry.comments;
        referenceMap[id] = comments.map((c) => c.body);
    }

    const total = Object.keys(answers).length;
    let i = 0;
    for (const [id, generated_comment] of Object.entries(answers)) {
        console.log(`Processing ${id}...`);
        if (!(id in referenceMap)) {
            // throw new Error(`id: "${id}" is not present in the dataset`);
            console.error(`id: "${id}" is not present in the dataset`);
            continue;
        }
        const references = referenceMap[id];

        let maxScore = 0;
        for (let reference of references) {
            const score = bleu(reference, generated_comment, 4); // TODO: ask prof what number show be here
            maxScore = Math.max(score, maxScore);
            console.log(`bleu score: ${score}`);
        }
        console.log(`Max bleu score: ${maxScore}`);

        console.log(`Done with ${id}`);
        percent_cb(Math.floor((++i / total) * 100));
    }
    console.log("Done processing comments!");
};

export const evaluate_refinement = async (answers, percent_cb) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        await new Promise((res) => setTimeout(res, 1000));
        console.log("Done");
        percent_cb(Math.floor((++i / total) * 100));
    }
};
