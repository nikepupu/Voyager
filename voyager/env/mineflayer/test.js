const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const mineflayer = require("mineflayer");

const skills = require("./lib/skillLoader");
const { initCounter, getNextTime } = require("./lib/utils");
const obs = require("./lib/observation/base");
const OnChat = require("./lib/observation/onChat");
const OnError = require("./lib/observation/onError");
const { Voxels, BlockRecords } = require("./lib/observation/voxels");
const Status = require("./lib/observation/status");
const Inventory = require("./lib/observation/inventory");
const OnSave = require("./lib/observation/onSave");
const Chests = require("./lib/observation/chests");
const Furnaces = require("./lib/observation/furnaces");
const { plugin: tool } = require("mineflayer-tool");

let bot1 = null;
let bot2 = null;
let bot3 = null;
port = 46693;

bot1 = null;
bot1 = mineflayer.createBot({
    host: "localhost", // minecraft server ip
    port: port, // minecraft server port
    username: "agent1", // minecraft username
    disableChatSigning: true,
    checkTimeoutInterval: 60 * 60 * 1000,
});

bot2 = mineflayer.createBot({
    host: "localhost", // minecraft server ip
    port: port, // minecraft server port
    username: "agent2", // minecraft username
    disableChatSigning: true,
    checkTimeoutInterval: 60 * 60 * 1000,
});

bot3 = mineflayer.createBot({
    host: "localhost", // minecraft server ip
    port: port, // minecraft server port
    username: "agent3", // minecraft username
    disableChatSigning: true,
    checkTimeoutInterval: 60 * 60 * 1000,
});

bot1.once("error", onConnectionFailed);
bot2.once("error", onConnectionFailed);

// Event subscriptions
bot1.waitTicks = 20;
bot1.globalTickCounter = 0;
bot1.stuckTickCounter = 0;
bot1.stuckPosList = [];
bot1.iron_pickaxe = false;
bot1.on("kicked", onDisconnect);

bot2.waitTicks = 20;
bot2.globalTickCounter = 0;
bot2.stuckTickCounter = 0;
bot2.stuckPosList = [];
bot2.iron_pickaxe = false;
bot2.on("kicked", onDisconnect);

if (bot3){
    bot3.waitTicks = 20;
    bot3.globalTickCounter = 0;
    bot3.stuckTickCounter = 0;
    bot3.stuckPosList = [];
    bot3.iron_pickaxe = false;
    bot3.on("kicked", onDisconnect);
}

// mounting will cause physicsTick to stop
bot1.on("mount", () => {
    bot1.dismount();
});

bot2.on("mount", () => {
    bot2.dismount();
});
if (bot3){
    bot3.on("mount", () => {
        bot3.dismount();
    });
}

bot1.once("spawn", async () => {
    bot1.removeListener("error", onConnectionFailed);
    let itemTicks = 1;
    
    bot1.chat("/clear @s");
    // bot1.chat("/kill @s");
    await bot1.waitForTicks(bot1.waitTicks * 3);
    bot2.chat("/clear @s");
    // bot2.chat("/kill @s");
    bot3.chat("/clear @s");

    

    const { pathfinder } = require("mineflayer-pathfinder");
    const tool = require("mineflayer-tool").plugin;
    const collectBlock = require("mineflayer-collectblock").plugin;
    const pvp = require("mineflayer-pvp").plugin;
    const minecraftHawkEye = require("minecrafthawkeye");
    bot1.loadPlugin(pathfinder);
    bot1.loadPlugin(tool);
    bot1.loadPlugin(collectBlock);
    bot1.loadPlugin(pvp);
    bot1.loadPlugin(minecraftHawkEye);

    obs.inject(bot1, [
        OnChat,
        OnError,
        Voxels,
        Status,
        Inventory,
        OnSave,
        Chests,
        BlockRecords,
        Furnaces,
    ]);
    skills.inject(bot1);


    await bot1.waitForTicks(bot1.waitTicks * itemTicks);

    initCounter(bot1);

    bot2.loadPlugin(pathfinder);
    bot2.loadPlugin(tool);
    bot2.loadPlugin(collectBlock);
    bot2.loadPlugin(pvp);
    bot2.loadPlugin(minecraftHawkEye);

    obs.inject(bot2, [
        OnChat,
        OnError,
        Voxels,
        Status,
        Inventory,
        OnSave,
        Chests,
        BlockRecords,
        Furnaces,
    ]);
    skills.inject(bot2);

    bot2.chat('/skin alex');

    bot3.loadPlugin(pathfinder);
    bot3.loadPlugin(tool);
    bot3.loadPlugin(collectBlock);
    bot3.loadPlugin(pvp);
    bot3.loadPlugin(minecraftHawkEye);
    obs.inject(bot3, [
        OnChat,
        OnError,
        Voxels,
        Status,
        Inventory,
        OnSave,
        Chests,
        BlockRecords,
        Furnaces,
    ]);
    skills.inject(bot3);
    

    await bot2.waitForTicks(bot2.waitTicks * itemTicks);
    await bot1.waitForTicks(bot1.waitTicks * itemTicks);

    // bot1.chat("/gamerule keepInventory true");
    // bot1.chat("/gamerule doDaylightCycle false");
});

function onConnectionFailed(e) {
    console.log(e);
    bot1 = null;
    bot2 = null;
    bot3 = null;
    res.status(400).json({ error: e });
}
function onDisconnect(message) {
    if (bot1.viewer) {
        bot1.viewer.close();
    }
    bot1.end();
    console.log(message);
    bot1 = null;

    if (bot2.viewer) {
        bot2.viewer.close();
    }
    bot2.end();
    console.log(message);
    bot2 = null;

    if (bot3.viewer) {
        bot3.viewer.close();
    }
    bot3.end();
    console.log(message);
    bot3 = null;
}
