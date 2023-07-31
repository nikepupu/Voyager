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

const app = express();

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.post("/start", (req, res) => {
    function setupbot(bot, index){
        if (bot) onDisconnect("Restarting bot1");
        bot = null;
        console.log(req.body);
        bot = mineflayer.createBot({
            host: "localhost", // minecraft server ip
            port: req.body.port, // minecraft server port
            username: "bot"+index,
            disableChatSigning: true,
            checkTimeoutInterval: 60 * 60 * 1000,
        });
        bot.once("error", onConnectionFailed);

        // Event subscriptions
        bot.waitTicks = req.body.waitTicks;
        bot.globalTickCounter = 0;
        bot.stuckTickCounter = 0;
        bot.stuckPosList = [];
        bot.iron_pickaxe = false;

        bot.on("kicked", onDisconnect);

        // mounting will cause physicsTick to stop
        bot.on("mount", () => {
            bot1.dismount();
        });

        bot.once("spawn", async () => {
            bot.removeListener("error", onConnectionFailed);
            let itemTicks = 1;
            if (req.body.reset === "hard") {
                bot.chat("/clear @s");
                bot.chat("/kill @s");
                const inventory = req.body.inventory ? req.body.inventory : {};
                const equipment = req.body.equipment
                    ? req.body.equipment
                    : [null, null, null, null, null, null];
                for (let key in inventory) {
                    bot.chat(`/give @s minecraft:${key} ${inventory[key]}`);
                    itemTicks += 1;
                }
                const equipmentNames = [
                    "armor.head",
                    "armor.chest",
                    "armor.legs",
                    "armor.feet",
                    "weapon.mainhand",
                    "weapon.offhand",
                ];
                for (let i = 0; i < 6; i++) {
                    if (i === 4) continue;
                    if (equipment[i]) {
                        bot.chat(
                            `/item replace entity @s ${equipmentNames[i]} with minecraft:${equipment[i]}`
                        );
                        itemTicks += 1;
                    }
                }
            }

            if (req.body.position) {
                bot.chat(
                    `/tp @s ${req.body.position.x} ${req.body.position.y} ${req.body.position.z}`
                );
            }

            // if iron_pickaxe is in bot1's inventory
            if (
                bot.inventory.items().find((item) => item.name === "iron_pickaxe")
            ) {
                bot.iron_pickaxe = true;
            }

            const { pathfinder } = require("mineflayer-pathfinder");
            const tool = require("mineflayer-tool").plugin;
            const collectBlock = require("mineflayer-collectblock").plugin;
            const pvp = require("mineflayer-pvp").plugin;
            const minecraftHawkEye = require("minecrafthawkeye");
            bot.loadPlugin(pathfinder);
            bot.loadPlugin(tool);
            bot.loadPlugin(collectBlock);
            bot.loadPlugin(pvp);
            bot.loadPlugin(minecraftHawkEye);

            // bot1.collectBlock.movements.digCost = 0;
            // bot1.collectBlock.movements.placeCost = 0;

            obs.inject(bot, [
                OnChat,
                OnError,
                Voxels,
                Status,
                Inventory,
                OnSave,
                Chests,
                BlockRecords,
            ]);
            skills.inject(bot);

            if (req.body.spread) {
                bot.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
                await bot.waitForTicks(bot.waitTicks);
            }

            await bot.waitForTicks(bot.waitTicks * itemTicks);
            res.json(bot.observe());

            initCounter(bot);
            bot.chat("/gamerule keepInventory true");
            bot.chat("/gamerule doDaylightCycle false");
        });
    }

    setupbot(bot1, 1);
    // setupbot(bot2, 2);

    function onConnectionFailed(e) {
        console.log(e);
        bot1 = null;
        res.status(400).json({ error: e });
    }
    function onDisconnect(message) {
        if (bot1.viewer) {
            bot1.viewer.close();
        }
        bot1.end();
        console.log(message);
        bot1 = null;
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
                res.json(bot1.observe());
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

    bot1.on("physicTick", onTick);

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
    await returnItems();
    // wait for last message
    await bot1.waitForTicks(bot1.waitTicks);
    if (!response_sent) {
        response_sent = true;
        res.json(bot1.observe());
    }
    bot1.removeListener("physicTick", onTick);

    async function evaluateCode(code, programs) {
        // Echo the code produced for players to see it. Don't echo when the bot1 code is already producing dialog or it will double echo
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

    function returnItems() {
        bot1.chat("/gamerule doTileDrops false");
        const crafting_table = bot1.findBlock({
            matching: mcData.blocksByName.crafting_table.id,
            maxDistance: 128,
        });
        if (crafting_table) {
            bot1.chat(
                `/setblock ${crafting_table.position.x} ${crafting_table.position.y} ${crafting_table.position.z} air destroy`
            );
            bot1.chat("/give @s crafting_table");
        }
        const furnace = bot1.findBlock({
            matching: mcData.blocksByName.furnace.id,
            maxDistance: 128,
        });
        if (furnace) {
            bot1.chat(
                `/setblock ${furnace.position.x} ${furnace.position.y} ${furnace.position.z} air destroy`
            );
            bot1.chat("/give @s furnace");
        }
        if (bot1.inventoryUsed() >= 32) {
            // if chest is not in bot1's inventory
            if (!bot1.inventory.items().find((item) => item.name === "chest")) {
                bot1.chat("/give @s chest");
            }
        }
        // if iron_pickaxe not in bot1's inventory and bot1.iron_pickaxe
        if (
            bot1.iron_pickaxe &&
            !bot1.inventory.items().find((item) => item.name === "iron_pickaxe")
        ) {
            bot1.chat("/give @s iron_pickaxe");
        }
        bot1.chat("/gamerule doTileDrops true");
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
    res.json({
        message: "bot1 stopped",
    });
});

app.post("/pause", (req, res) => {
    if (!bot1) {
        res.status(400).json({ error: "bot1 not spawned" });
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
