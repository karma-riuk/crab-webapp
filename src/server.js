import express, { json } from "express";
import cors from "cors";
import dotenv from "dotenv";
import routes from "./routes/index.js";
import { createSocketServer } from "./socket.js";

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(json());

// Use routes
app.use(express.static("public"));
app.use("/", routes);

const server = createSocketServer(app);

// Start server
server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
