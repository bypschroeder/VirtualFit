import { z } from "zod";

const MAX_FILE_SIZE = 1024 * 1024 * 5; // 5MB
const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png"];

export const generateSchema = z.object({
	gender: z.enum(["male", "female"]),
	height: z.coerce.number().min(140).max(220),
	weight: z.coerce.number().min(40).max(120),
	image: z
		.any()
		.refine(
			(file) => file?.size <= MAX_FILE_SIZE,
			"Image size should be less than 5MB"
		)
		.refine(
			(file) => ACCEPTED_IMAGE_TYPES.includes(file?.type),
			"Invalid image type. Only JPEG and PNG are accepted"
		),
});

export const tryonSchema = z.object({
	obj: z
		.preprocess(
			(val) => (val === undefined || val === null ? null : val),
			z.instanceof(File).refine((file) => file.name.endsWith(".obj"), {
				message: "Please upload a valid .obj file.",
			})
		)
		.refine((val) => val !== null, {
			message: "Please upload a file.",
		}),
	garment: z.preprocess(
		(val) => (val === undefined || val === null ? null : val),
		z.enum(["t-shirt", "sweatshirt", "hoodie"], {
			required_error: "Please select a garment",
		})
	),
	gender: z.enum(["male", "female"]),
	size: z.enum(["XS", "S", "M", "L", "XL", "XXL"]),
});
