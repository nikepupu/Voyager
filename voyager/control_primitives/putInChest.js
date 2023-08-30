function itemToString (item) {
    if (item) {
      return `${item.name} x ${item.count}`
    } else {
      return '(nothing)'
    }
  }

async function putInChest(bot, itemToDepositName) {

    const chestBlock = bot.findBlock({
        matching: mcData.blocksByName.chest.id,
        maxDistance: 32,
    });
    if (!chestBlock) {
        throw new Error("No chest nearby");
    } else {
        await bot.pathfinder.goto(
            new GoalLookAtBlock(chestBlock.position, bot.world)
        );
    }
    
    if (chestBlock) {
        const chest = bot.openChest(chestBlock);
    }

    const itemByName = mcData.itemsByName[itemToDepositName];
    if (!itemByName) {
        bot.chat(`No item named ${itemToDepositName}`);
        return
    }
    const item = bot.inventory.findInventoryItem(itemByName.id);
    if (!item) {
        bot.chat(`No ${itemToDepositName} in inventory`);
        let items = bot.inventory.items();
        bot.chat('Inventory: ');
        const output = items.map(itemToString).join(', ');
        bot.chat('Inventory: ');
        bot.chat(output);
        if (output) {
            bot.chat(output)
          } else {
            bot.chat('empty')
          }
        return;
    }
    else {
        try {
            await chest.deposit(item.type, null, 1);
        } catch (err) {
            bot.chat(`Not enough ${itemToDepositName} in inventory.`);
        }   
    }
}
