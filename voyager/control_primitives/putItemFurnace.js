async function putItemFurnace(bot, itemName) {
    // return if itemName or fuelName is not string
    if (typeof itemName !== "string" ) {
        throw new Error("itemName for smeltItem must be a string");
    }
    // return if count is not a number
    const item = mcData.itemsByName[itemName];
    
    if (!item) {
        throw new Error(`No item named ${itemName}`);
    }

    const furnaceBlock = bot.findBlock({
        matching: mcData.blocksByName.furnace.id,
        maxDistance: 32,
    });
    const furnace = await bot.openFurnace(furnaceBlock);
    
    if (!bot.inventory.findInventoryItem(item.id, null)) {
        bot.chat(`No ${itemName} to smelt in inventory`);
        furnace.close();
        return
    }
    
    await furnace.putInput(item.id, null, 1);
    
    await bot.waitForTicks(12 * 40);
    

    bot1.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    bot2.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    await furnace.close();
}
