CREATE TABLE IF NOT EXISTS `warlord`.`users` (
    `user_id` INT NOT NULL AUTO_INCREMENT ,
    `last_updated` TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    `discord` VARCHAR(50) NOT NULL ,
    `username` VARCHAR(50) NOT NULL ,
    `faction` ENUM('Syndicate','Marauder','Covenant','') NOT NULL ,
    `company` VARCHAR(50) NULL DEFAULT NULL ,
    `level` INT NOT NULL ,
    `role` VARCHAR(20) NOT NULL ,
    `weapon1` VARCHAR(50) NOT NULL ,
    `weapon2` VARCHAR(50) NOT NULL ,
    `extra` TEXT NULL DEFAULT NULL ,
    `edit_key` VARCHAR(100) NULL DEFAULT NULL ,
    PRIMARY KEY (`user_id`),
    UNIQUE `user` (`discord`)
)
ENGINE = InnoDB
CHARSET = utf8mb4
COLLATE utf8mb4_general_ci;