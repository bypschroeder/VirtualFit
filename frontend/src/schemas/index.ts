import { z } from "zod";

const MAX_FILE_SIZE = 1024 * 1024 * 1; // 5MB
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
