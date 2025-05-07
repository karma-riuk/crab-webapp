import http from "http";
import { Server } from "socket.io";

function onConnect(socket) {
    console.log("Websocket client connected:", socket.id);
}

export function createSocketServer(app) {
    const httpServer = http.createServer(app);
    const io = new Server(httpServer);
    io.on("connection", onConnect);
    app.set("io", io);
    return httpServer;
}
