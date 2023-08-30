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
const { plugin: tool } = require("mineflayer-tool");

let bot1 = null;
let bot2 = null;
function clearBotInventory(bot){
    // Iterate through the bot's inventory slots
    bot.inventory.slots.forEach((slot, index) => {
      if (slot) {
        bot.tossStack(slot, (err) => {
          if (err) {
            console.error(`Error tossing item from slot ${index}:`, err);
          }
        });
      }
    });

}

function moveHeldItemToInventory() {
const heldItem1 = bot1.heldItem;

if (!heldItem1) {
    bot1.chat("Bot isn't holding any item.");
    return;
}

// Find first empty slot in the main inventory (excluding hotbar)
let firstEmptySlotIndex = bot1.inventory.slots.slice(9, 36).findIndex(slot => !slot);

if (firstEmptySlotIndex === -1) {
    bot1.chat("No empty slot found in the main inventory.");
    return;
}

// Move the held item to the first empty slot in the main inventory
bot1.inventory.move(bot1.quickBarSlot, firstEmptySlotIndex + 9);

const heldItem2 = bot2.heldItem;
if (!heldItem2) {
    bot2.chat("Bot isn't holding any item.");
    return;
    }

    // Find first empty slot in the main inventory (excluding hotbar)
firstEmptySlotIndex = bot2.inventory.slots.slice(9, 36).findIndex(slot => !slot);

    if (firstEmptySlotIndex === -1) {
    bot2.chat("No empty slot found in the main inventory.");
    return;
    }

    // Move the held item to the first empty slot in the main inventory
    bot2.inventory.move(bot2.quickBarSlot, firstEmptySlotIndex + 9);

}

if (bot1) onDisconnect("Restarting bot");
bot1 = mineflayer.createBot({
    host: "localhost", // minecraft server ip
    port: req.body.port, // minecraft server port
    username: "bot" + PORT, // minecraft username
    disableChatSigning: true,
    checkTimeoutInterval: 60 * 60 * 1000,
});

bot2 = mineflayer.createBot({
    host: "localhost", // minecraft server ip
    port: req.body.port, // minecraft server port
    username: "bot" + PORT+2, // minecraft username
    disableChatSigning: true,
    checkTimeoutInterval: 60 * 60 * 1000,
});

bot1.once("error", onConnectionFailed);
bot2.once("error", onConnectionFailed);

// Event subscriptions
bot1.waitTicks = req.body.waitTicks;
bot1.globalTickCounter = 0;
bot1.stuckTickCounter = 0;
bot1.stuckPosList = [];
bot1.iron_pickaxe = false;
bot1.on("kicked", onDisconnect);

bot2.waitTicks = req.body.waitTicks;
bot2.globalTickCounter = 0;
bot2.stuckTickCounter = 0;
bot2.stuckPosList = [];
bot2.iron_pickaxe = false;
bot2.on("kicked", onDisconnect);

// mounting will cause physicsTick to stop
bot1.on("mount", () => {
    bot1.dismount();
});

bot2.on("mount", () => {
    bot2.dismount();
});

let promises = [];

bot1.once("spawn", async () => {

    promises.push(new Promise(async (resolve) => {
        bot1.removeListener("error", onConnectionFailed);
        let itemTicks = 1;
        
        bot1.chat("/clear @s");
        bot1.chat("/kill @s");
        

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
        ]);
        skills.inject(bot1);

        if (req.body.spread) {
            bot1.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot1.waitForTicks(bot1.waitTicks);
        }

        await bot1.waitForTicks(bot1.waitTicks * itemTicks);

        initCounter(bot1);
        // return_data = str([bot1.observe(), bot2.observe()])
        moveHeldItemToInventory(bot1);
        clearBotInventory(bot1);
        await bot1.waitForTicks(bot1.waitTicks * itemTicks);
        resolve();
    }));
});

bot2.once("spawn", async () => {
    promises.push(new Promise(async (resolve) => {
        bot2.chat("/clear @s");
        bot2.chat("/kill @s");
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
        ]);
        skills.inject(bot2);

        if (req.body.spread) {
            bot2.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot2.waitForTicks(bot2.waitTicks);
        }

        initCounter(bot2);
        moveHeldItemToInventory(bot2);
        clearBotInventory(bot2);
        await bot2.waitForTicks(bot2.waitTicks * itemTicks);
        resolve();
    }));

}); 

const thirdCallback = () => {
    res.json({bot1: bot1.observe(), bot2: bot2.observe()});
}

Promise.all(promises).then(() => {
    res.json({bot1: bot1.observe(), bot2: bot2.observe()});
});

function onConnectionFailed(e) {
    console.log(e);
    bot1 = null;
    bot2 = null;
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
}


