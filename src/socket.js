import http from "http";
import { Server } from "socket.io";

function onConnect(socket) {
    console.log("Websocket client connected:", socket.id);
}

let io;

function createSocketServer(app) {
    const httpServer = http.createServer(app);
    io = new Server(httpServer);
    io.on("connection", onConnect);
    return httpServer;
}

export { createSocketServer, io };
