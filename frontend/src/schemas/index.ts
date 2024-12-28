import { z } from "zod";

export const generateSchema = z.object({
	gender: z.enum(["male", "neutral", "female"]),
	height: z.coerce.number().min(140).max(220),
	weight: z.coerce.number().min(40).max(120),
	image: z.any(),
});
