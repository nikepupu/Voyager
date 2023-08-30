const mineflayer = require('mineflayer');

const skills = require("./voyager/env/mineflayer/lib/skillLoader");
const { initCounter, getNextTime } = require("./voyager/env/mineflayer/lib/utils");
const obs = require("./voyager/env/mineflayer/lib/observation/base");
const OnChat = require("./voyager/env/mineflayer/lib/observation/onChat");
const OnError = require("./voyager/env/mineflayer/lib/observation/onError");
const { Voxels, BlockRecords } = require("./voyager/env/mineflayer/lib/observation/voxels");
const Status = require("./voyager/env/mineflayer/lib/observation/status");
const Inventory = require("./voyager/env/mineflayer/lib/observation/inventory");
const OnSave = require("./voyager/env/mineflayer/lib/observation/onSave");
const Chests = require("./voyager/env/mineflayer/lib/observation/chests");
const { plugin: tool } = require("mineflayer-tool");
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

function onConnectionFailed1(e) {
    console.log(e);
    // bot1 = null;
    res.status(400).json({ error: e });
}
function onConnectionFailed2(e) {
    console.log(e);
    // bot2 = null;
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

const bot1 = mineflayer.createBot({
  host: 'localhost',     // Minecraft server IP or address
  port: 44401,           // Optional, default is 25565
  username: 'BotUsername', // Minecraft username of the bot
  // password: 'password',   // If the server is online-mode
});

const bot2 = mineflayer.createBot({
    host: 'localhost',     // Minecraft server IP or address
    port: 44401,           // Optional, default is 25565
    username: 'BotUsername2', // Minecraft username of the bot
    // password: 'password',   // If the server is online-mode
  });

let promises = [];

bot1.once('spawn', () => {
    promises.push(new Promise(async (resolve) => {
        bot1.removeListener("error", onConnectionFailed1);
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


        await bot1.waitForTicks(bot1.waitTicks * itemTicks);

        initCounter(bot1);
        // return_data = str([bot1.observe(), bot2.observe()])
        moveHeldItemToInventory(bot1);
        clearBotInventory(bot1);
        await bot1.waitForTicks(bot1.waitTicks * itemTicks);
        resolve();
    }));
  
});

bot2.once('spawn', () => {
    promises.push(new Promise(async (resolve) => {
        bot2.removeListener("error", onConnectionFailed2);
        let itemTicks = 1;
        
        bot2.chat("/clear @s");
        bot2.chat("/kill @s");
        

        const { pathfinder } = require("mineflayer-pathfinder");
        const tool = require("mineflayer-tool").plugin;
        const collectBlock = require("mineflayer-collectblock").plugin;
        const pvp = require("mineflayer-pvp").plugin;
        const minecraftHawkEye = require("minecrafthawkeye");
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


        await bot2.waitForTicks(bot2.waitTicks * itemTicks);

        initCounter(bot2);
        // return_data = str([bot1.observe(), bot2.observe()])
        moveHeldItemToInventory(bot2);
        clearBotInventory(bot2);
        await bot2.waitForTicks(bot2.waitTicks * itemTicks);
        resolve();
    }));
  
});

Promise.all(promises).then(() => {
    bot1.chat("/clear @s");
});