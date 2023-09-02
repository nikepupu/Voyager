function arePositionsAlmostEqual(pos1, pos2, threshold = 1) {
    return Math.abs(pos1.x - pos2.x) <= threshold &&
           Math.abs(pos1.y - pos2.y) <= threshold &&
           Math.abs(pos1.z - pos2.z) <= threshold;
}

async function updateEntities(bot, level) {
    if (level == 1) {
        const entities = [
            {
                name: 'sheep',
                position: new Vec3(-5, -60, -10)
            },
            {
                name: 'chicken',
                position: new Vec3(-3, -60, -10)
            }
        ];
    }
    

    for(let entity of entities) {
        let target_pos = entity.position;
        let name = entity.name;
        let block = bot.blockAt(target_pos);

        if ( !block || block.name !== name) {
            if (name === 'sheep') {
                bot.chat('/summon sheep ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1, DeathLootTable:"minecraft:entities/sheep/mutton",DeathLootTableSeed:-12345}');
            } else if (name === 'chicken') {
                bot.chat('/summon chicken ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1, DeathLootTable:"minecraft:entities/chicken",DeathLootTableSeed:-1234}');
            }
        }
     
    }

}
