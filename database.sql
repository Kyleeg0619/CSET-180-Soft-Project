CREATE DATABASE  IF NOT EXISTS `egarden` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `egarden`;
-- MySQL dump 10.13  Distrib 8.0.27, for Win64 (x86_64)
--
-- Host: localhost    Database: egarden
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `cart_item_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `size` varchar(100) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cart_item_id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (17,4,17,'Small','Yellow',2,6.25,'2025-05-13 16:10:16'),(18,4,12,'Large','Blue',3,35.00,'2025-05-13 16:11:15'),(19,4,15,'Medium','Purple',9,11.99,'2025-05-13 16:11:32'),(27,5,10,'Small','Yellow',1,5.00,'2025-05-13 16:22:14'),(28,5,10,'Small','Yellow',1,5.00,'2025-05-13 16:22:25'),(38,6,11,'Medium','Green',2,12.00,'2025-05-13 16:37:04'),(41,7,14,'Medium','Purple',1,7.50,'2025-05-13 16:42:42'),(45,12,9,'Medium','Red',1,14.50,'2025-05-13 18:51:48');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `recipient_id` int NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `recipient_id` (`recipient_id`),
  CONSTRAINT `chat_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `chat_ibfk_2` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat`
--

LOCK TABLES `chat` WRITE;
/*!40000 ALTER TABLE `chat` DISABLE KEYS */;
INSERT INTO `chat` VALUES (5,4,3,'I loved your product!','2025-05-05 22:45:09'),(6,4,5,'love ur stuff!','2025-05-05 23:01:14'),(7,4,6,'thanks for the quality product!','2025-05-06 08:58:30'),(8,4,6,'yippe','2025-05-06 09:40:42'),(13,5,10,'Hello, I really liked the tulips and will be recommending to my family!','2025-05-13 13:15:45'),(16,10,5,'Thank You!','2025-05-13 14:39:14'),(17,12,10,'Hi, I loved the roses!','2025-05-13 14:51:35');
/*!40000 ALTER TABLE `chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `order_date` datetime DEFAULT NULL,
  `complaint_date` datetime DEFAULT NULL,
  `complaint_title` text,
  `complaint_desc` text,
  `complaint_demand` text,
  `complaint_status` varchar(20) DEFAULT 'pending',
  PRIMARY KEY (`complaint_id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (22,9,'2025-05-13 12:22:03','2025-05-13 00:00:00','Request to Return Damaged Plant from Order','I received my order, one of the plants (Purple Heart Wandering Jew) arrived damaged and unhealthy. The leaves were wilted and several stems were broken. I followed all care instructions but the plant has not recovered. I would like to request a return or replacement. Photos of the condition on arrival are attached.\r\n\r\n','refund','pending'),(23,8,'2025-05-13 12:20:41','2025-05-13 00:00:00','Warranty Claim for Unhealthy Plant','Despite proper care as outlined in the instructions, the plant (Purple Heart Wandering Jew) has deteriorated significantly within the warranty period. Leaves are discolored and wilting, and the plant shows no signs of recovery. I have attached photos showing the current condition. Please advise on the next steps for a replacement or refund under the warranty policy.','warranty','rejected'),(24,12,'2025-05-13 12:36:53','2025-05-13 00:00:00','Warranty Claim for Damaged Plant Upon Arrival','The plant I received was in poor condition on arrival, with broken stems and wilted leaves. I followed the recommended care instructions, but it did not recover. I am requesting a replacement under the warranty policy. Photos are attached for reference.\r\n\r\n','warranty','confirmed'),(25,11,'2025-05-13 12:35:48','2025-05-13 00:00:00','Plant Declined Despite Proper Care','After receiving the plant, I ensured it had proper light, water, and drainage. However, it began wilting and showing signs of rot within a week. I’m filing a warranty claim for a replacement or refund based on the plant health guarantee.\r\n\r\n','return','complete'),(26,13,'2025-05-13 12:42:32','2025-05-13 00:00:00','Refund Request for Damaged Plant','The plant I received arrived damaged, with broken stems and wilted leaves. I do not wish to receive a replacement and would prefer a refund instead. I’ve attached photos to support the request.','refund','confirmed'),(27,13,'2025-05-13 12:42:32','2025-05-13 00:00:00','Plant Did Not Survive – Refund Requested','Despite following all care instructions, the plant declined rapidly and died within days of arrival. I’d like to request a refund under the store’s live arrival or plant health guarantee. Photo evidence is attached.\r\n\r\n','return','rejected'),(28,14,'2025-05-13 14:49:19','2025-05-13 00:00:00','I did not mean to order the roses!','I\'m so sorry, please refund me.','refund','pending');
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `address` varchar(500) DEFAULT NULL,
  `payment_info` varchar(255) DEFAULT NULL,
  `order_date` datetime DEFAULT NULL,
  `total_items` int DEFAULT NULL,
  `order_status` varchar(25) DEFAULT 'pending',
  `vendor_usernames` varchar(40) DEFAULT NULL,
  `item_list` text,
  PRIMARY KEY (`order_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (7,4,'Jason Bobson','888 Balls Street','8888 3333 8888 4444','2025-05-13 11:55:22',5,'pending',NULL,'9,10,13,14,16'),(8,5,'Jennifer Carson','383 James Ave','3333 4444 5555 6666','2025-05-13 12:20:41',3,'shipped',NULL,'13,12,18'),(9,5,'Jennifer Carson','383 James Ave','8888 3333 8888 4444','2025-05-13 12:22:03',4,'confirmed',NULL,'15,9,11,14'),(10,8,'Kevin Y','355 Simpson Ave','3333 3333 3333 6666','2025-05-13 12:27:41',3,'shipped',NULL,'9,18,10'),(11,6,'Brian Walls','333 Arran Ave','8888 5655 8888 4444','2025-05-13 12:35:48',3,'confirmed',NULL,'11,12,16'),(12,6,'Brian Walls','333 Arran Ave','3333 4444 5555 6666','2025-05-13 12:36:53',3,'handed',NULL,'13,10,17'),(13,7,'Emily Tams','322 Abs Ave','8888 3333 8888 4444','2025-05-13 12:42:32',2,'pending',NULL,'11,14'),(14,12,'Alice Benson','383 James Ave','3333 4444 5555 6666','2025-05-13 14:49:19',3,'pending',NULL,'9,12,13');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_reviews`
--

DROP TABLE IF EXISTS `product_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `review_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `review_title` text,
  `review_desc` text,
  PRIMARY KEY (`review_id`),
  CONSTRAINT `reviews_chk_prod` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_reviews`
--

LOCK TABLES `product_reviews` WRITE;
/*!40000 ALTER TABLE `product_reviews` DISABLE KEYS */;
INSERT INTO `product_reviews` VALUES (4,4,9,5,'2025-05-13 12:03:05','Beautiful Red Velvet Rose Seeds','Seeds sprouted well and grew into healthy plants with stunning deep red blooms. Easy to follow instructions, good germination rate, and lovely results. Great for home gardens!'),(5,4,14,5,'2025-05-13 12:05:10','Vibrant and Easy to Grow!','The Purple Heart Wandering Jew arrived healthy and well-packaged. The deep purple leaves are beautiful, and it started growing quickly with minimal care. Perfect as a houseplant or outdoor accent. Very low maintenance and great for beginners!'),(6,4,10,2,'2025-05-13 12:07:50','Disappointed with Germination','Unfortunately, only a few of the Sunny Marigold seeds sprouted, even with proper soil, watering, and full sun. The ones that did grow were weak and didn’t bloom as expected. Disappointing experience compared to other seed packs I’ve used. Would not buy again from this seller.'),(7,8,9,2,'2025-05-13 12:28:12','Poor Germination and No Blooms','I was really excited to grow these Red Velvet Roses, but the results were disappointing. Out of the whole packet, only a couple of seeds sprouted. Despite following all the planting instructions, the seedlings stayed small and never produced any flowers. Not worth the money — I won’t be buying these again.'),(8,8,10,5,'2025-05-13 12:28:45','Easy to Grow and Full of Color!','These Sunny Marigold seeds were a joy to plant! Almost all of them sprouted quickly, and within weeks I had strong, healthy plants. The blooms are bright, cheerful, and lasted a long time. Great for borders and keeping pests away. Perfect for beginner gardeners too—definitely buying again!'),(9,8,18,3,'2025-05-13 12:29:22','Pretty Plant, But a Bit Fussy','The Ruby Rubber Plant arrived in decent condition with beautiful variegated leaves, but it took a while to adjust. Some leaves dropped in the first week, and it needed just the right light and watering to bounce back. It’s a nice plant, but not as low-maintenance as I expected. Good for experienced plant parents.'),(10,8,9,4,'2025-05-13 12:30:18','Gorgeous Blooms with a Bit of Patience','The Red Velvet Rose seeds took some time to germinate, but once they did, the plants grew strong and healthy. The blooms are rich, velvety red and absolutely stunning. They require regular care and plenty of sunlight, but the results are worth it. Just not ideal if you\'re looking for something low-maintenance.'),(11,8,9,5,'2025-05-13 12:30:41','Stunning Roses and Great Quality Seeds','Absolutely loved these Red Velvet Rose seeds! Nearly all of them germinated, and the plants grew into strong, healthy bushes. The deep red blooms are vibrant, velvety, and smell amazing. With regular care, they flourished beautifully. Perfect addition to my garden—highly recommend!'),(12,7,14,5,'2025-05-13 12:43:39','Vibrant Color and Super Easy to Grow','I ordered the Purple Heart Wandering Jew from eGarden and couldn’t be happier. The plant arrived healthy and well-packaged, with deep purple foliage that looks even better in person. It adjusted quickly and has been growing fast with very little maintenance. Perfect for hanging baskets or as ground cover. Great value and a beautiful addition to my collection!\r\n\r\n'),(13,12,9,5,'2025-05-13 14:49:55','I loved the roses','They make my garden look even better!');
/*!40000 ALTER TABLE `product_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(40) NOT NULL,
  `product_desc` varchar(255) DEFAULT NULL,
  `product_color` text,
  `product_sizes` text,
  `product_quantity` int NOT NULL,
  `original_price` decimal(6,2) NOT NULL,
  `discount_price` decimal(6,2) DEFAULT NULL,
  `product_warranty` date DEFAULT NULL,
  `vendor_username` varchar(20) DEFAULT NULL,
  `discount_date_end` date DEFAULT NULL,
  PRIMARY KEY (`product_id`),
  KEY `vendor_username` (`vendor_username`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`vendor_username`) REFERENCES `users` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (9,'Red Velvet Rose','A classic romantic rose with deep red petals and a strong fragrance.','Red,Purple','Medium',1,18.00,14.50,'2025-05-29','Ashleysroses','2025-05-17'),(10,'Sunny Marigold','Bright yellow marigolds perfect for borders and pest control.','Yellow,Green','Small,Medium',45,5.00,NULL,NULL,'Ashleysroses',NULL),(11,'Blue Star Fern','Elegant blue-green ferns with arching fronds and low-maintenance needs.','Green,Blue','Small,Medium,Large',12,16.00,12.00,'2025-05-23','Ashleysroses','2025-05-15'),(12,'Blue Agave','A hardy succulent known for its striking blue-green foliage.','Blue,Purple','Large',4,35.00,NULL,NULL,'Mikesblooms',NULL),(13,'Lemon Balm','A lemon-scented herb used in teas and natural remedies.','Yellow,Green','Small',20,6.50,NULL,NULL,'Mikesblooms',NULL),(14,'Purple Heart Wandering Jew','Bold purple trailing plant, great for hanging baskets or ground cover.','Purple','Medium',4,10.00,7.50,'2025-05-13','Mikesblooms','2025-05-24'),(15,'Lavender Dream','Fragrant lavender blooms that attract pollinators and calm the senses.','Purple','Medium',24,15.00,11.99,NULL,'Sarassucculents',NULL),(16,'Scarlet Coleus','Vivid red and green foliage ideal for shade gardens or containers.','Red,Yellow','Medium',22,12.00,9.00,NULL,'Sarassucculents',NULL),(17,'Yellow Dwarf Sunflower','Compact sunflowers bursting with golden blooms, perfect for pots.','Yellow','Small,Medium',33,8.00,6.25,'2025-06-06','Sarassucculents','2025-05-14'),(18,'Ruby Rubber Plant','A trendy indoor plant with burgundy-red and dark green waxy leaves.','Red','Large',7,28.00,NULL,NULL,'Sarassucculents',NULL),(19,'Lavender Plant','Lavender seedling directly from Arizona, Ethically farmed and sourced.','Purple','Medium',15,15.00,10.00,'2025-06-07','Mikesblooms','2025-06-03');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `review_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `review_title` text,
  `review_desc` text,
  PRIMARY KEY (`review_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `reviews_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (3,8,5,'2025-05-13 12:32:10','Fantastic Online Plant Shopping Experience!','I’ve had a wonderful experience shopping on eGarden. The website is easy to navigate, and I love how they have a wide variety of plants, from common favorites to rare finds. The descriptions for each plant are detailed, and the photos are accurate. My orders always arrive on time and in great condition, and the customer service is responsive if I have questions. I’ve bought multiple plants, and every one has thrived! Definitely my go-to for all things plants.'),(4,6,4,'2025-05-13 12:39:49','Great Selection, Fast Delivery','eGarden has a fantastic selection of plants at reasonable prices. The website is user-friendly, making it easy to find what you’re looking for. My plants arrived quickly and were packaged securely. The only reason I’m not giving 5 stars is that one of my plants arrived slightly damaged, but customer service was quick to resolve it. Overall, a great experience and I’ll be back for more!'),(5,7,5,'2025-05-13 12:44:05','Reliable and Enjoyable Plant Shopping Experience','eGarden is one of the best plant shopping sites I’ve used. The layout is clean and easy to navigate, with clear categories and helpful filters. Product pages include detailed care instructions and realistic photos, which make choosing plants simple. Checkout was smooth, and my order arrived on time in great condition. I also appreciate the chat support feature—it’s helpful and responsive. eGarden makes online plant shopping fun, easy, and trustworthy. Highly recommend for beginners and seasoned plant lovers alike!\r\n\r\n'),(6,12,5,'2025-05-13 14:50:23','I had such a great ordering experience!','Will be ordering again!');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(20) DEFAULT NULL,
  `last_name` varchar(20) DEFAULT NULL,
  `user_type` varchar(20) NOT NULL,
  `email` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (4,'Jasonb','scrypt:32768:8:1$0KJFJJhsY8AKJ6Wt$8073eff003a414653a02f8834a05776edbfa89c6a87d5390a309af65d639c957ffdec6f6573bc0e19a45b12d41fb08064434d3d378bddf17669599274c55bc79','Jason','Bobson','Customer','Jasonb@gmail.com'),(5,'Jenniferc','scrypt:32768:8:1$JOgkXnOxwX2nEDQj$a32eb55736b873c66fdf0654b8f4f2fb64b293f202d50a2ac0394c59a5c2e5ab41dd0e56724aadf6852a0e540b922ad8720333935ed0cc2ed01cfb31398d1f3d','Jennifer','Carson','Customer','Jenniferc@gmail.com'),(6,'Brainw','scrypt:32768:8:1$vQJzZdoEfU9PUY10$6afcdd014e6ddae595b1d0c82fdd7387313e8c8d79edf7b4ae74e8b7547e02e8c2da02e9f82a49d3f8d4821f69abd15ea392fec9f954dc3fbc649337eb8a2381','Brain','Walls','Customer','Brainw@gmail.com'),(7,'Emilyt','scrypt:32768:8:1$0is08nTq1sFQXjXG$e03d84cbc5b46066e35a65e64d951a822eb6070d0b2e7d30b3c3f5221caeb7719d8ecf8f79ae9bfdbd613acd718298d92bf1cd43443df5398a66676bc723acac','Emily','Tams','Customer','emilyt@gmail.com'),(8,'Keviny','scrypt:32768:8:1$jBP2hP5hGuFRFBfl$c7ab59834b316bd80e20e7318df438f10f50d0b18ff8375c990e7f84d8245672d963e925bf404a6a5717eb0c7dcae83a06bf41634f5472b556b5e31d78e7361d','Kevin','Yenava','Customer','Keviny@gmail.com'),(9,'Ashleysroses','scrypt:32768:8:1$e8snmG4uBs32hMj0$a2482eaf31afd53d057fa033f45b05cdb9df34884dfb84b80f0d5366ef1cd37b03910b559f8117d762532c14d481fe98c8379fc04274cf6ceef5b7bff7c99a1b','Ashley','Throns','Vendor','ash@gmail.com'),(10,'Mikesblooms','scrypt:32768:8:1$smdSzgEM87hXkt95$03c4e8670b96e72ad52dceb2eb8dfc0984407d2b323549d2ba67ec6bc0dc7a8c5669e21e308b9d51fe064ea31d243159ff85683182fe811ae2decfaa941c0f36','Mike','Johnson','Vendor','mikeb@gmail.com'),(11,'Sarassucculents','scrypt:32768:8:1$sHz2dfr5IlNGOIVF$bfd994fc48fa159bd4e0e865e91b39af5959df1cc4e6bc094d6bcc8047823aefd595e669ebd6430e11ee01149609394ce6f355a75c21bd61e37581e5e0a9e55e','Sara','Adams','Vendor','saras@gmail.com'),(12,'Ashleyr','scrypt:32768:8:1$JGSTgHXy39LMrkE1$0dc2ee65f9df9f262bdfb78400d66ec3075d0129efd14002b06faad06e7b841cf96a43dfa6488abec3adc0cc071ede5c4c134082e7093536e672fa0550ad547e','Ashley','Rose','Customer','ashleyr@gmail.com');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'egarden'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-13 15:21:24
