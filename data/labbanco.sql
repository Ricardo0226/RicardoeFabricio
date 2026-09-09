SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


CREATE SCHEMA IF NOT EXISTS `LabAgenda` DEFAULT CHARACTER SET utf8 ;
USE `LabAgenda` ;


CREATE TABLE IF NOT EXISTS `LabAgenda`.`professor` (
  `area` VARCHAR(100) NULL,
  `nome` VARCHAR(100) NULL,
  `matricula` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`matricula`),
  UNIQUE INDEX `matricula_UNIQUE` (`matricula` ASC) VISIBLE)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `LabAgenda`.`curso` (
  `nome` VARCHAR(100) NULL,
  `abreviaçao` VARCHAR(5) NULL,
  `codigo` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`codigo`),
  UNIQUE INDEX `codigo_UNIQUE` (`codigo` ASC) VISIBLE)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `LabAgenda`.`disciplina` (
  `nome` VARCHAR(100) NULL,
  `codigo` VARCHAR(50) NOT NULL,
  `ch` INT NULL,
  UNIQUE INDEX `codigo_UNIQUE` (`codigo` ASC) VISIBLE,
  PRIMARY KEY (`codigo`),
  CONSTRAINT `tem`
    FOREIGN KEY (`codigo`)
    REFERENCES `LabAgenda`.`curso` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `LabAgenda`.`lab` (
  `capacidade` VARCHAR(100) NULL,
  `numero` VARCHAR(50) NOT NULL,
  `descriçao` VARCHAR(10000) NULL,
  `status` VARCHAR(20) NULL,
  PRIMARY KEY (`numero`),
  UNIQUE INDEX `numero_UNIQUE` (`numero` ASC) VISIBLE)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `LabAgenda`.`professor_disciplina` (
  `matricula_professor` VARCHAR(50) NOT NULL,
  `codigo_disciplina` VARCHAR(50) NOT NULL,
  `ano` VARCHAR(45) NULL,
  `semestre` VARCHAR(45) NULL,
  PRIMARY KEY (`matricula_professor`, `codigo_disciplina`),
  CONSTRAINT `ministra`
    FOREIGN KEY (`matricula_professor`)
    REFERENCES `LabAgenda`.`professor` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ministraa`
    FOREIGN KEY (`codigo_disciplina`)
    REFERENCES `LabAgenda`.`disciplina` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `LabAgenda`.`disciplina_lab` (
  `codigo_disciplina` VARCHAR(50) NOT NULL,
  `lab_numero` VARCHAR(50) NOT NULL,
  `ano` VARCHAR(45) NULL,
  `semestre` VARCHAR(45) NULL,
  PRIMARY KEY (`codigo_disciplina`, `lab_numero`),
  CONSTRAINT `usa`
    FOREIGN KEY (`lab_numero`)
    REFERENCES `LabAgenda`.`lab` (`numero`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `usaa`
    FOREIGN KEY (`codigo_disciplina`)
    REFERENCES `LabAgenda`.`disciplina` (`codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


INSERT INTO `LabAgenda`.`professor` (`area`, `nome`, `matricula`)
VALUES 
('Informática', 'Gilbran de Andrade', '3567818'),
('Informática', 'Diogo Eugenio', '4330507');


INSERT INTO `LabAgenda`.`disciplina` (`nome`, `codigo`, `ch`)
VALUES 
('AWEB', 'D001', 80),
('Banco de Dados', 'D002', 80),
('Redes de Computadores', 'D004', 100),
('Projeto Integrador', 'D003', 80);


INSERT INTO `LabAgenda`.`professor_disciplina` (`matricula_professor`, `codigo_disciplina`, `ano`, `semestre`)
VALUES
('3567818', 'D001', '2025', '1'),
('3567818', 'D002', '2025', '1'),
('3567818', 'D003', '2025', '1'),
('4330507', 'D002', '2025', '1'),
('4330507', 'D004', '2025', '1');


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


CREATE TABLE IF NOT EXISTS `LabAgenda`.`agendamento` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `laboratorio` VARCHAR(50) NOT NULL,
  `professor_matricula` VARCHAR(50) NOT NULL,
  `disciplina_nome` VARCHAR(100) NOT NULL,
  `dia_semana` INT NOT NULL,
  `horario_periodo` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `unique_agendamento` (`laboratorio` ASC, `dia_semana` ASC, `horario_periodo` ASC) VISIBLE,
  CONSTRAINT `fk_agendamento_lab`
    FOREIGN KEY (`laboratorio`)
    REFERENCES `LabAgenda`.`lab` (`numero`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_agendamento_professor`
    FOREIGN KEY (`professor_matricula`)
    REFERENCES `LabAgenda`.`professor` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);