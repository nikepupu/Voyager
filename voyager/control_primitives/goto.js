async function goto(bot, locationName) {
    const blockByName = mcData.blocksByName[locationName];
    let block; // Define block here so it's in the outer scope.

    if (locationName == 'furnace') {
        block = bot.findBlock({
            matching: blockByName.id,
            maxDistance: 32,
        });
    } else if (['sheep', 'chicken'].includes(locationName)) {
        block = bot.nearestEntity(
            (entity) =>
                entity.name === locationName && // Change mobName to locationName
                entity.position.distanceTo(bot.entity.position) < 48
        );
    }
    
    if (!block) {
        throw new Error("No " + locationName + " nearby");
    } else {
        await bot.pathfinder.goto(
            new GoalLookAtBlock(block.position, bot.world)
        );
    }
}