import { Router } from "express";
import multer from "multer";
import { InvalidJsonFormatError } from "../utils/errors.js";
import { evaluate_comments } from "../utils/process_data.js";

const router = Router();

// Configure multer for file uploads
const upload = multer({
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 200 * 1024 * 1024, // 200MB limit, since the comement gen is 147MB (deflated)
    },
    fileFilter: (_req, file, cb) => {
        // Accept only JSON files
        if (file.mimetype === "application/json") {
            cb(null, true);
        } else {
            cb(new Error("Only JSON files are allowed"));
        }
    },
});

// Helper function to validate JSON format
const validateJsonFormat = (data) => {
    try {
        const parsed = JSON.parse(data);
        // Check if it's an object
        if (
            typeof parsed !== "object" ||
            parsed === null ||
            Array.isArray(parsed)
        ) {
            throw new InvalidJsonFormatError(
                "Submitted json doesn't contain an object",
            );
        }
        // Check if all values are strings
        if (
            !Object.values(parsed).every((value) => typeof value === "string")
        ) {
            throw new InvalidJsonFormatError(
                "Submitted json object must only be str -> str. Namely id -> comment",
            );
        }
        return parsed;
    } catch (error) {
        if (error instanceof InvalidJsonFormatError) {
            throw error;
        }
        throw new InvalidJsonFormatError("Invalid JSON format");
    }
};

router.post("/submit/comments", upload.single("file"), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }

        const fileContent = req.file.buffer.toString();
        let validatedData;

        try {
            validatedData = validateJsonFormat(fileContent);
        } catch (error) {
            if (error instanceof InvalidJsonFormatError) {
                return res.status(400).json({
                    error: "Invalid JSON format",
                    message: error.message,
                });
            }
            throw error;
        }

        const io = req.app.get("io");
        const header = req.get("X-Socket-Id");
        const socketId = header && header.trim();
        if (socketId && io.sockets.sockets.has(socketId)) {
            io.to(socketId).emit("successul-upload");
            io.to(socketId).emit("started-processing");
        }

        const results = evaluate_comments(validatedData, (percent) => {
            if (!(socketId && io.sockets.sockets.has(socketId))) return;

            io.to(socketId).emit("progress", { percent });
        });
        res.status(200).json(results);
    } catch (error) {
        console.error("Error processing submission:", error);
        res.status(500).json({ error: "Error processing submission" });
    }
});

router.post("/submit/refinement", upload.single("file"), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }

        const fileContent = req.file.buffer.toString();
        let validatedData;

        try {
            validatedData = validateJsonFormat(fileContent);
        } catch (error) {
            if (error instanceof InvalidJsonFormatError) {
                return res.status(400).json({
                    error: "Invalid JSON format",
                    message: error.message,
                });
            }
            throw error;
        }

        socket.emit("started-processing");
        evaluate_comments(validatedData);
        res.status(200).json({
            message: "Answer submitted successfully",
            data: validatedData,
        });
    } catch (error) {
        console.error("Error processing submission:", error);
        res.status(500).json({ error: "Error processing submission" });
    }
});

export default router;
