CREATE DATABASE IF NOT EXISTS `aes` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `aes`;

CREATE TABLE IF NOT EXISTS `cuentas` (
	`id` BIGINT NOT NULL AUTO_INCREMENT,
  	`usuario` varchar(50) NOT NULL UNIQUE,
  	`contrasena` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

INSERT INTO `cuentas` ( `usuario`, `contrasena`) VALUES ('gibran', 'b7eccd0059d6d7dc2ef76c35d6de0048cc8c029d');