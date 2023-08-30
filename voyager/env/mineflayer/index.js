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
const app = express();

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.post("/start", (req, res) => {
    if (bot1) onDisconnect("Restarting bot");
    bot1 = null;
    console.log(req.body);
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

    bot1.once("spawn", async () => {
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
        

        await bot2.waitForTicks(bot2.waitTicks * itemTicks);
        await bot1.waitForTicks(bot1.waitTicks * itemTicks);
        // return_data = str([bot1.observe(), bot2.observe()])
        moveHeldItemToInventory(bot1);
        moveHeldItemToInventory(bot2);
        clearBotInventory(bot1);
        clearBotInventory(bot2);
        await bot2.waitForTicks(bot2.waitTicks * itemTicks);
        await bot1.waitForTicks(bot1.waitTicks * itemTicks);

        res.json({bot1: bot1.observe(), bot2: bot2.observe()});

        // bot1.chat("/gamerule keepInventory true");
        // bot1.chat("/gamerule doDaylightCycle false");
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
});

app.post("/step", async (req, res) => {
    // import useful package
    let response_sent = false;
    function otherError(err) {
        console.log("Uncaught Error");
        bot1.emit("error", handleError(err));
        bot1.waitForTicks(bot1.waitTicks).then(() => {
            if (!response_sent) {
                response_sent = true;
                res.json({bot1: bot1.observe(), bot2: bot2.observe()});
            }
        });
    }

    process.on("uncaughtException", otherError);

    const mcData = require("minecraft-data")(bot1.version);
    mcData.itemsByName["leather_cap"] = mcData.itemsByName["leather_helmet"];
    mcData.itemsByName["leather_tunic"] =
        mcData.itemsByName["leather_chestplate"];
    mcData.itemsByName["leather_pants"] =
        mcData.itemsByName["leather_leggings"];
    mcData.itemsByName["leather_boots"] = mcData.itemsByName["leather_boots"];
    mcData.itemsByName["lapis_lazuli_ore"] = mcData.itemsByName["lapis_ore"];
    mcData.blocksByName["lapis_lazuli_ore"] = mcData.blocksByName["lapis_ore"];
    const {
        Movements,
        goals: {
            Goal,
            GoalBlock,
            GoalNear,
            GoalXZ,
            GoalNearXZ,
            GoalY,
            GoalGetToBlock,
            GoalLookAtBlock,
            GoalBreakBlock,
            GoalCompositeAny,
            GoalCompositeAll,
            GoalInvert,
            GoalFollow,
            GoalPlaceBlock,
        },
        pathfinder,
        Move,
        ComputedPath,
        PartiallyComputedPath,
        XZCoordinates,
        XYZCoordinates,
        SafeBlock,
        GoalPlaceBlockOptions,
    } = require("mineflayer-pathfinder");
    const { Vec3 } = require("vec3");

    // Set up pathfinder
    const movements = new Movements(bot1, mcData);
    bot1.pathfinder.setMovements(movements);

    bot1.globalTickCounter = 0;
    bot1.stuckTickCounter = 0;
    bot1.stuckPosList = [];

    function onTick() {
        bot1.globalTickCounter++;
        if (bot1.pathfinder.isMoving()) {
            bot1.stuckTickCounter++;
            if (bot1.stuckTickCounter >= 100) {
                onStuck(1.5);
                bot1.stuckTickCounter = 0;
            }
        }
    }

    function onTick2() {
        bot2.globalTickCounter++;
        if (bot2.pathfinder.isMoving()) {
            bot2.stuckTickCounter++;
            if (bot2.stuckTickCounter >= 100) {
                onStuck2(1.5);
                bot2.stuckTickCounter = 0;
            }
        }
    }

    bot1.on("physicTick", onTick);
    bot2.on("physicTick", onTick2);
    // initialize fail count
    let _craftItemFailCount = 0;
    let _killMobFailCount = 0;
    let _mineBlockFailCount = 0;
    let _placeItemFailCount = 0;
    let _smeltItemFailCount = 0;

    // Retrieve array form post bod
    const code = req.body.code;
    const programs = req.body.programs;
    bot1.cumulativeObs = [];
    await bot1.waitForTicks(bot1.waitTicks);
    const r = await evaluateCode(code, programs);
    process.off("uncaughtException", otherError);
    if (r !== "success") {
        bot1.emit("error", handleError(r));
    }
    // await returnItems();
    // wait for last message
    await bot1.waitForTicks(bot1.waitTicks);
    if (!response_sent) {
        response_sent = true;
        res.json({bot1: bot1.observe(), bot2: bot2.observe()});
    }
    bot1.removeListener("physicTick", onTick);
    bot2.removeListener("physicTick", onTick2);

    async function evaluateCode(code, programs) {
        // Echo the code produced for players to see it. Don't echo when the bot code is already producing dialog or it will double echo
        try {
            await eval("(async () => {" + programs + "\n" + code + "})()");
            return "success";
        } catch (err) {
            return err;
        }
    }

    function onStuck(posThreshold) {
        const currentPos = bot1.entity.position;
        bot1.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot1.stuckPosList.length === 5) {
            const oldestPos = bot1.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot(); // execute the function
            }

            // Remove the oldest time from the list
            bot1.stuckPosList.shift();
        }
    }
    function onStuck2(posThreshold) {
        const currentPos = bot2.entity.position;
        bot2.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot2.stuckPosList.length === 5) {
            const oldestPos = bot2.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot2(); // execute the function
            }

            // Remove the oldest time from the list
            bot2.stuckPosList.shift();
        }
    }

    function teleportBot() {
        const blocks = bot1.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot1.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot1.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function teleportBot2() {
        const blocks = bot2.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot2.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot2.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function handleError(err) {
        let stack = err.stack;
        if (!stack) {
            return err;
        }
        console.log(stack);
        const final_line = stack.split("\n")[1];
        const regex = /<anonymous>:(\d+):\d+\)/;

        const programs_length = programs.split("\n").length;
        let match_line = null;
        for (const line of stack.split("\n")) {
            const match = regex.exec(line);
            if (match) {
                const line_num = parseInt(match[1]);
                if (line_num >= programs_length) {
                    match_line = line_num - programs_length;
                    break;
                }
            }
        }
        if (!match_line) {
            return err.message;
        }
        let f_line = final_line.match(
            /\((?<file>.*):(?<line>\d+):(?<pos>\d+)\)/
        );
        if (f_line && f_line.groups && fs.existsSync(f_line.groups.file)) {
            const { file, line, pos } = f_line.groups;
            const f = fs.readFileSync(file, "utf8").split("\n");
            // let filename = file.match(/(?<=node_modules\\)(.*)/)[1];
            let source = file + `:${line}\n${f[line - 1].trim()}\n `;

            const code_source =
                "at " +
                code.split("\n")[match_line - 1].trim() +
                " in your code";
            return source + err.message + "\n" + code_source;
        } else if (
            f_line &&
            f_line.groups &&
            f_line.groups.file.includes("<anonymous>")
        ) {
            const { file, line, pos } = f_line.groups;
            let source =
                "Your code" +
                `:${match_line}\n${code.split("\n")[match_line - 1].trim()}\n `;
            let code_source = "";
            if (line < programs_length) {
                source =
                    "In your program code: " +
                    programs.split("\n")[line - 1].trim() +
                    "\n";
                code_source = `at line ${match_line}:${code
                    .split("\n")
                    [match_line - 1].trim()} in your code`;
            }
            return source + err.message + "\n" + code_source;
        }
        return err.message;
    }
    
});

app.post("/stop", (req, res) => {
    bot1.end();
    bot2.end();
    res.json({
        message: "Bot stopped",
    });
});

app.post("/pause", (req, res) => {
    if (!bot1 || !bot2) {
        res.status(400).json({ error: "Bot not spawned" });
        return;
    }
    bot1.chat("/pause");
    bot1.waitForTicks(bot1.waitTicks).then(() => {
        res.json({ message: "Success" });
    });
});

// Server listening to PORT 3000

const DEFAULT_PORT = 3000;
const PORT = process.argv[2] || DEFAULT_PORT;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
