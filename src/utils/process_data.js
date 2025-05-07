export const evaluate_comments = async (answers, percent_cb) => {
    const total = Object.keys(answers).length;
    let i = 0;
    for (const [key, value] of Object.entries(answers)) {
        console.log(`Processing ${key}: ${value}...`);
        await new Promise((res) => setTimeout(res, 1000));
        console.log("Done");
        percent_cb(Math.floor((++i / total) * 100));
    }
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
