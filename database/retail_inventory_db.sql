CREATE DATABASE IF NOT EXISTS `retail_inventory_2`
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE `retail_inventory_2`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `transaction`;
DROP TABLE IF EXISTS `product`;
DROP TABLE IF EXISTS `category`;
DROP TABLE IF EXISTS `password_reset`;
DROP TABLE IF EXISTS `user`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `user` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `fullName` varchar(120) DEFAULT NULL,
  `businessName` varchar(120) DEFAULT NULL,
  `businessType` varchar(80) DEFAULT NULL,
  `password` varchar(260) NOT NULL,
  `privacyConsent` tinyint(1) NOT NULL DEFAULT 0,
  `privacyConsentAt` datetime DEFAULT NULL,
  `privacyNoticeVersion` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `password_reset` (
  `resetID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `tokenHash` varchar(260) NOT NULL,
  `expiresAt` datetime NOT NULL,
  `usedAt` datetime DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`resetID`),
  KEY `fk_password_reset_user` (`userID`),
  CONSTRAINT `fk_password_reset_user` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `category` (
  `categoryID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `userID` int NOT NULL,
  PRIMARY KEY (`categoryID`),
  UNIQUE KEY `category_user_unique` (`name`, `userID`),
  KEY `fk_category_user` (`userID`),
  CONSTRAINT `fk_category_user` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `product` (
  `productID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `stock` int NOT NULL DEFAULT 0,
  `userID` int NOT NULL,
  `categoryID` int DEFAULT NULL,
  `costPrice` decimal(10,2) NOT NULL DEFAULT 0,
  `salePrice` decimal(10,2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`productID`),
  KEY `fk_product_user` (`userID`),
  KEY `fk_product_category` (`categoryID`),
  CONSTRAINT `fk_product_user` FOREIGN KEY (`userID`) REFERENCES `user` (`userID`),
  CONSTRAINT `fk_product_category` FOREIGN KEY (`categoryID`) REFERENCES `category` (`categoryID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transaction` (
  `transactionID` int NOT NULL AUTO_INCREMENT,
  `type` varchar(45) NOT NULL,
  `timestamp` datetime NOT NULL,
  `productID` int NOT NULL,
  `amount` int DEFAULT 0,
  `totalValue` decimal(10,2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`transactionID`),
  KEY `fk_transaction_product` (`productID`),
  CONSTRAINT `fk_transaction_product` FOREIGN KEY (`productID`) REFERENCES `product` (`productID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user`
(`userID`, `username`, `email`, `fullName`, `businessName`, `businessType`, `password`, `privacyConsent`, `privacyConsentAt`, `privacyNoticeVersion`)
VALUES
(1, 'Felix', 'felix@example.com', 'Felix', 'Demo Retail', 'Electronics retail', 'f6b6aad7a7690810466cb5288aea79c4eccd72d05bae7ab16be65bf9b3b6538e', 1, '2026-06-02 00:00:00', 'UK-GDPR-2026-06');

INSERT INTO `category` (`categoryID`, `name`, `userID`) VALUES
(1, 'Laptops', 1),
(2, 'Phones', 1),
(3, 'Gaming', 1);

INSERT INTO `product` (`productID`, `name`, `stock`, `userID`, `categoryID`, `costPrice`, `salePrice`) VALUES
(1, 'Macbook Air 2025', 5, 1, 1, 850.00, 999.00),
(3, 'Macbook Air 2024', 3, 1, 1, 700.00, 849.00),
(4, 'iPhone 17 Pro Max', 100, 1, 2, 900.00, 1199.00),
(5, 'Xbox Series X', 0, 1, 3, 390.00, 479.00),
(6, 'Xbox Series S', 500, 1, 3, 220.00, 279.00);

INSERT INTO `transaction` (`transactionID`, `type`, `timestamp`, `productID`, `amount`, `totalValue`) VALUES
(1, 'purchase', '2026-03-31 11:16:16', 1, 5, 4250.00),
(2, 'purchase', '2026-03-31 11:35:27', 3, 3, 2100.00),
(5, 'sell', '2026-03-31 11:44:37', 1, 1, 999.00),
(6, 'sell', '2026-03-31 12:14:39', 3, 1, 849.00),
(7, 'purchase', '2026-03-31 12:15:26', 4, 100, 90000.00),
(8, 'sell', '2026-03-31 12:17:01', 4, 1, 1199.00),
(9, 'restock', '2026-03-31 12:39:42', 4, 10, 9000.00),
(10, 'purchase', '2026-03-31 12:45:23', 5, 1, 390.00),
(11, 'sell', '2026-03-31 12:50:51', 5, 1, 479.00),
(12, 'restock', '2026-03-31 12:54:20', 5, 2, 780.00),
(13, 'sell', '2026-03-31 12:55:16', 5, 1, 479.00),
(14, 'purchase', '2026-03-31 12:58:24', 6, 500, 110000.00);
