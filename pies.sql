-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 11-07-2024 a las 22:00:26
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.0.28

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
-- Estructura de tabla para la tabla `configuraciones`
--

CREATE TABLE `configuraciones` (
  `id` int(5) NOT NULL,
  `lowerH` int(5) NOT NULL,
  `lowerS` int(5) NOT NULL,
  `lowerV` int(5) NOT NULL,
  `upperH` int(5) NOT NULL,
  `upperS` int(5) NOT NULL,
  `upperV` int(5) NOT NULL,
  `lowerHdedos` int(5) NOT NULL,
  `lowerSdedos` int(5) NOT NULL,
  `lowerVdedos` int(5) NOT NULL,
  `upperHdedos` int(5) NOT NULL,
  `upperSdedos` int(5) NOT NULL,
  `upperVdedos` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `configuraciones`
--

INSERT INTO `configuraciones` (`id`, `lowerH`, `lowerS`, `lowerV`, `upperH`, `upperS`, `upperV`, `lowerHdedos`, `lowerSdedos`, `lowerVdedos`, `upperHdedos`, `upperSdedos`, `upperVdedos`) VALUES
(1, 13, 15, 42, 125, 255, 255, 64, 46, 22, 92, 255, 255);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `plantillas`
--

CREATE TABLE `plantillas` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text NOT NULL,
  `fecha` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `plantillas`
--

INSERT INTO `plantillas` (`id`, `nombre`, `descripcion`, `fecha`) VALUES
(1, 'Pie plano', 'Con un porcentaje entre 0 al 34%', NULL),
(2, 'Pie plano/normal', 'Con un porcentaje entre 35% al 39%', NULL),
(3, 'Pie normal', 'Con un porcentaje entre 40% al 54%', NULL),
(4, 'Pie normal/cavo', 'Con un porcentaje entre 55% al 59%', NULL),
(5, 'Pie cavo', 'Con un porcentaje entre 60% al 74%', NULL),
(6, 'Pie cavo fuerte', 'Con un porcentaje entre 75% al 84%', NULL),
(7, 'Pie cavo extremo', 'Con un porcentaje entre 85% al 100%', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pruebas`
--

CREATE TABLE `pruebas` (
  `id` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `x_izquierdo` varchar(10) NOT NULL,
  `y_izquierdo` varchar(10) NOT NULL,
  `porcentaje_izquierda` varchar(10) NOT NULL,
  `id_plantilla_izquierda` varchar(50) NOT NULL,
  `x_derecha` varchar(10) NOT NULL,
  `y_derecha` varchar(10) NOT NULL,
  `porcentaje_derecha` varchar(10) NOT NULL,
  `id_plantilla_derecha` varchar(50) NOT NULL,
  `foto` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Volcado de datos para la tabla `pruebas`
--

INSERT INTO `pruebas` (`id`, `id_usuario`, `x_izquierdo`, `y_izquierdo`, `porcentaje_izquierda`, `id_plantilla_izquierda`, `x_derecha`, `y_derecha`, `porcentaje_derecha`, `id_plantilla_derecha`, `foto`, `fecha`) VALUES
(5, 20, '6.84328797', '3.36883729', '51%', 'Pie normal', '6.46430939', '4.16622047', '64%', 'Pie cavo', 'static/usuarios/0604655654/fotos/procesada/4_imagen_procesada.png', '2024-07-11 18:11:00'),
(6, 20, '6.84328797', '3.36883729', '51%', 'Pie normal', '6.46430939', '4.16622047', '64%', 'Pie cavo', 'static/usuarios/0604655654/fotos/procesada/1_imagen_procesada.png', '2024-07-11 18:12:03'),
(7, 20, '6.84328797', '3.36883729', '51%', 'Pie normal', '6.46430939', '4.16622047', '64%', 'Pie cavo', 'static/usuarios/0604655654/fotos/procesada/2_imagen_procesada.png', '2024-07-11 18:16:20'),
(8, 20, '6.84328797', '3.36883729', '51%', 'Pie normal', '6.46430939', '4.16622047', '64%', 'Pie cavo', 'static/usuarios/0604655654/fotos/procesada/3_imagen_procesada.png', '2024-07-11 19:05:34');

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
(20, 'Sebas Cuenca', '0604655654', '0983133440', '1.75', '29', '85', 'masculino', 'usuarios/0604655654/fotos/perfil/perfil.png', '2024-07-11 05:13:01');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `plantillas`
--
ALTER TABLE `plantillas`
  ADD PRIMARY KEY (`id`);

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
-- AUTO_INCREMENT de la tabla `plantillas`
--
ALTER TABLE `plantillas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `pruebas`
--
ALTER TABLE `pruebas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
