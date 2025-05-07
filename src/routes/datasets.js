import { Router } from "express";
import { join } from "path";
import { getProjectPath } from "../utils/paths.js";

const router = Router();

// Environment variables for paths (all relative to project root)
const DATA_DIR = process.env.DATA_DIR
    ? getProjectPath(process.env.DATA_DIR)
    : getProjectPath("data");

const DATASETS = ["comment_generation", "code_refinement"];

router.get("/download/:dataset", async (req, res) => {
    const { dataset } = req.params;
    const withContext = req.query.withContext
        ? JSON.parse(req.query.withContext)
        : false;

    if (!DATASETS.includes(dataset)) {
        return res.status(400).json({ error: "Invalid dataset name" });
    }

    const fileName = `${dataset}_${withContext ? "with_context" : "no_context"}.zip`;
    const filePath = join(DATA_DIR, fileName);

    try {
        res.download(filePath);
    } catch (error) {
        console.error("Error serving file:", error);
        res.status(500).json({ error: "Error serving file" });
    }
});

export default router;
