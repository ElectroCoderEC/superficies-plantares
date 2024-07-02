-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 03-07-2024 a las 01:01:19
-- Versión del servidor: 10.4.27-MariaDB
-- Versión de PHP: 8.0.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `pies`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pruebas`
--

CREATE TABLE `pruebas` (
  `id` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `foto` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `cedula` varchar(10) NOT NULL,
  `telefono` varchar(13) NOT NULL,
  `estatura` varchar(10) NOT NULL,
  `edad` varchar(10) NOT NULL,
  `peso` varchar(10) NOT NULL,
  `genero` varchar(20) NOT NULL,
  `imagen` text NOT NULL,
  `fecha` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `cedula`, `telefono`, `estatura`, `edad`, `peso`, `genero`, `imagen`, `fecha`) VALUES
(1, 'Sebas Cuenca', '091283821', '09831732', '1.75', '30', '90', 'masculino', '', '2024-07-01 22:38:01'),
(2, 'Andrea gomez', '912893289', '12321312', '1.60', '20', '50', 'femenino', '', '2024-07-02 03:32:09'),
(3, 'Juan Perez', 'asd', '21321', '1.60', '25', '70', 'masculino', '', '2024-07-02 03:57:20'),
(4, 'Prueba nube', '1231', '123', '1.50', '22', '50', 'masculino', '', '2024-07-02 04:02:11'),
(5, 'Prueba nube', '1231', '123', '1.50', '22', '50', 'masculino', '', '2024-07-02 04:02:11'),
(6, 'paola', '1232', '12321', '1.65', '23', '50', 'femenino', '', '2024-07-02 04:14:55'),
(8, 'Juan Perez', '21', '12', '12', '12', '12', 'masculino', '', '2024-07-02 04:18:36'),
(9, 'Prueba nube12', '1232', '09831732', '1.60', '21', '50', 'masculino', '', '2024-07-02 04:20:00'),
(10, 'asd', 'asd', 'asd', 'asd', '12', 'asd', 'masculino', '', '2024-07-02 04:24:39');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `pruebas`
--
ALTER TABLE `pruebas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `pruebas`
--
ALTER TABLE `pruebas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `pruebas`
--
ALTER TABLE `pruebas`
  ADD CONSTRAINT `pruebas_ibfk_1` FOREIGN KEY (`id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
