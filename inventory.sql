-- phpMyAdmin SQL Dump
-- version 4.8.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 07, 2018 at 06:18 PM
-- Server version: 10.1.31-MariaDB
-- PHP Version: 7.1.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `inventory`
--

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `vendor` varchar(20) NOT NULL,
  `mrp` int(11) NOT NULL,
  `batch_num` int(11) NOT NULL,
  `batch_date` varchar(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `status` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `vendor`, `mrp`, `batch_num`, `batch_date`, `quantity`, `status`) VALUES
(15, 'product 1 ', 'vendor 1', 33, 210, '2001-01-01', 66, 'Approved'),
(16, 'product 2', 'vendor 2 ', 200, 120, '2002-02-02', 10, 'Approved'),
(17, 'product 3', 'vendor 3', 75, 220, '2001-03-03', 100, 'Approved'),
(18, 'sdsfsf', 'sdfs', 322, 3332, '1999-01-01', 2, 'Approved');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `role` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `email`, `role`) VALUES
(8, 'srihari', '$5$rounds=535000$98xuxZpw0e8Av5ko$ll9RsUWOBFsBRf7h34GnEXj0pa7gpa.AfYjAfSRu.kC', 'srihari@manager.com', 0),
(9, 'srihari_assist', '$5$rounds=535000$Vold3gcd2NCzM.Qz$zS/m8FO6U.l1U.ABpvVRQu4ly302EGxUs2r/q9wUrwA', 'srihari@assist.com', 1),
(10, 'test', '$5$rounds=535000$3nFJwwi5qA2iZQBn$CeaczheJXqVGnSDu/3h8VPYs6vx8p6oNiATLuZwQjPD', 'test@test.com', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`,`name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
