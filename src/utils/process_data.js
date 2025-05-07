import { io as socket } from "../socket.js";

export const evaluate_comments = async (answers) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        await new Promise((res) => setTimeout(res, 500));
        console.log("Done");
        const data = {
            percent: Math.floor((++i / total) * 100),
        };
        socket.emit("progress", data);
    }
};

export const evaluate_refinement = async (answers) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        await new Promise((res) => setTimeout(res, 500));
        console.log("Done");
        const data = {
            percent: Math.floor((++i / total) * 100),
        };
        socket.emit("progress", data);
    }
};
