async function putFuelFurnace(bot, fuelName) {
    // return if itemName or fuelName is not string
    if ( typeof fuelName !== "string") {
        throw new Error("fuelName must be a string");
    }
    // return if count is not a number
   
    const fuel = mcData.itemsByName[fuelName];
    
    if (!fuel) {
        throw new Error(`No item named ${fuelName}`);
    }
    
    const furnaceBlock = bot.findBlock({
        matching: mcData.blocksByName.furnace.id,
        maxDistance: 48,
    });
    
    const furnace = await bot.openFurnace(furnaceBlock);
 
   
    if (!bot.inventory.findInventoryItem(fuel.id, null)) {
        bot.chat(`No ${fuelName} as fuel in inventory`);
        furnace.close();
        return
    }
    await furnace.putFuel(fuel.id, null, 1);
   
    await bot.waitForTicks(20);
    if (!furnace.fuel && furnace.fuelItem()?.name !== fuelName) {
        throw new Error(`${fuelName} is not a valid fuel`);
    }
   
    
    await bot.waitForTicks(12 * 40);

    bot1.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    bot2.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    await furnace.close();

}
