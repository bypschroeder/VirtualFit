import { generateSchema } from "@/schemas";
import { ChangeEvent } from "react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

export const handleDownload = (
	modelData: string | null,
	isFitted: boolean = false
) => {
	if (!modelData) {
		console.error("No model available for download");
		return;
	}

	const blob = new Blob([modelData as string], {
		type: "text/plain;charset=utf-8",
	});
	const url = URL.createObjectURL(blob);

	const a = document.createElement("a");
	a.href = url;
	const fileName = isFitted ? "fitted_model.obj" : "base_model.obj";
	a.download = fileName;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);

	URL.revokeObjectURL(url);
};

export const handleReset = (
	setObj: (obj: string | null) => void,
	setFitObj: (fitObj: string | null) => void,
	setImage: (image: string | null) => void
) => {
	setObj(null);
	setFitObj(null);
	setImage(null);
};

export const handleResetImage = (
	setObj: (obj: string | null) => void,
	setFitObj: (fitObj: string | null) => void,
	setImage: (image: string | null) => void,
	setGenerationError: (error: string | null) => void
) => {
	setObj(null);
	setFitObj(null);
	setImage(null);
	setGenerationError(null);
};

export const handleImageUpload = (
	event: ChangeEvent<HTMLInputElement>,
	setImage: (image: string | null) => void,
	form: UseFormReturn<z.infer<typeof generateSchema>>
) => {
	const file = event.target.files?.[0];
	if (file) {
		const maxSizeInBytes = 1024 * 1024 * 5; // 5MB
		if (file.size > maxSizeInBytes) {
			alert("Image size exceeds 5MB");
			return;
		}

		const reader = new FileReader();
		reader.onload = () => {
			if (typeof reader.result === "string") {
				setImage(reader.result);
			}
		};
		form.setValue("image", file);
		reader.readAsDataURL(file);
	}
};
