-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: 23-Out-2017 às 14:51
-- Versão do servidor: 5.7.20
-- PHP Version: 7.0.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `tts`
--
CREATE DATABASE IF NOT EXISTS `tts` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `tts`;

-- --------------------------------------------------------

--
-- Estrutura da tabela `faculty`
--

DROP TABLE IF EXISTS `faculty`;
CREATE TABLE `faculty` (
  `id` int(11) NOT NULL,
  `acronym` varchar(10) DEFAULT NULL,
  `name` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `faculty`
--
ALTER TABLE `faculty`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `acronym` (`acronym`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `faculty`
--
ALTER TABLE `faculty`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;
COMMIT;