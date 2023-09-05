function arePositionsAlmostEqual(pos1, pos2, threshold = 1) {
    return Math.abs(pos1.x - pos2.x) <= threshold &&
           Math.abs(pos1.y - pos2.y) <= threshold &&
           Math.abs(pos1.z - pos2.z) <= threshold;
}

async function updateEntities(bot, level) {
    let entitiesList = [];
    let voxel_list = [];
    if (level == '1') {
        entitiesList = [
            {
                name: 'sheep',
                position: new Vec3(-5, -60, -10)
            },
            {
                name: 'chicken',
                position: new Vec3(-3, -60, -10)
            }
        ];
        voxel_list = [
            {
                name: 'oak_log',
                position: new Vec3(2, -60, 4)
            }
        ]

    } else if (level == '2') {
        entitiesList = [
            {
                name: 'pig',
                position: new Vec3(-229, 32, -110)
            },
            {
                name: 'cow',
                position: new Vec3(-248, 32, -111)
            },
            {
                name: 'cow',
                position: new Vec3(-226, 32, -90)
            },
            {
                name: 'sheep',
                position: new Vec3(-245, 32, -105)
            },
            {
                name: 'sheep',
                position: new Vec3(-250, 32, -103)
            },
            {
                name: 'sheep',
                position: new Vec3(-248, 32, -107)
            },
            {
                name: 'sheep',
                position: new Vec3(-239, 32, -89)
            },
            {
                name: 'chicken',
                position: new Vec3(-245, 32, -108)
            },
            {
                name: 'chicken',
                position: new Vec3(-247, 32, -110)
            },
            {
                name: 'chicken',
                position: new Vec3(-239, 32, -108)
            },
            {
                name: 'chicken',
                position: new Vec3(-231, 32, -102)
            },
            {
                name: 'chicken',
                position: new Vec3(-229, 32, -89)
            },
            {
                name: 'chicken',
                position: new Vec3(-230, 32, -91)
            },
            {
                name: 'pig',
                position: new Vec3(-238, 32, -94)
            },

        ];
        voxel_list = [
            {
                name: 'oak_log',
                position: new Vec3(-227, 32, -107)
            }
        ]
    }
    care_about_entities = ['sheep', 'chicken', 'oak_log', 'pig', 'cow'];

    for(let entity_target of entitiesList) {
        let target_pos = entity_target.position;
        let name = entity_target.name;

        const entities = bot.entities;
        if (!entities) break;
    
        found = false;
        for (const id in entities) {
            const entity = entities[id];
            if (!entity.displayName) continue;
            if (entity.name === "player" || entity.name === "item") continue;
            if (entity.name === name && entity.position.distanceTo(target_pos) < 2) {
                found = true;
                break;
            }
        }
        if (!found) {
            if (name === 'sheep') {
                bot.chat('/summon sheep ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1}');
            } else if (name === 'chicken') {
                bot.chat('/summon chicken ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1, DeathLootTable:"minecraft:entities/chicken",DeathLootTableSeed:-1234}');
            } else if (name == 'pig') {
                bot.chat('/summon pig ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1}');
            } else if (name == 'cow') {
                bot.chat('/summon cow ' + target_pos.x + ' ' + target_pos.y + ' ' + target_pos.z + ' {NoAI:1}');
            }
        }
     
    }

    for (let voxel_target of voxel_list) {
        let target_pos = voxel_target.position;
        let name = voxel_target.name;
        let block = bot.blockAt(target_pos);
        if (!block || block.name !== name) {
            bot.chat(`/setblock ${target_pos.x} ${target_pos.y} ${target_pos.z} ${name}`);
        }
    }

}
