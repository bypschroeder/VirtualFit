import { generateSchema } from "@/schemas";
import JSZip from "jszip";
import { ChangeEvent } from "react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

export const handleDownload = async (
	modelData: string | null,
	mtlData: string | null,
	isFitted: boolean = false
) => {
	if (!modelData) {
		console.error("No model available for download");
		return;
	}

	if (isFitted && !mtlData) {
		console.error("No MTL data available for fitted model");
		return;
	}

	if (isFitted && mtlData) {
		const objResponse = await fetch(modelData);
		if (!objResponse.ok) {
			console.error("Failed to fetch fitted model");
			return;
		}
		const obj = await objResponse.text();

		const mtlResponse = await fetch(mtlData);
		if (!mtlResponse.ok) {
			console.error("Failed to fetch fitted model");
			return;
		}
		const mtl = await mtlResponse.text();

		const zip = new JSZip();
		zip.file("fitted_model.obj", obj);
		zip.file("fitted_model.mtl", mtl);

		const zipBlob = await zip.generateAsync({ type: "blob" });
		const zipUrl = URL.createObjectURL(zipBlob);

		const a = document.createElement("a");
		a.href = zipUrl;
		a.download = "fitted_model.zip";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(zipUrl);
	} else {
		const blob = new Blob([modelData as string], {
			type: "text/plain;charset=utf-8",
		});
		const url = URL.createObjectURL(blob);

		const a = document.createElement("a");
		a.href = url;
		a.download = "base_model.obj";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(url);
	}
};

export const handleReset = (
	setObj: (obj: string | null) => void,
	setFitObj: (fitObj: string | null) => void,
	setFitMtl: (fitMtl: string | null) => void,
	setImage: (image: string | null) => void
) => {
	setObj(null);
	setFitObj(null);
	setFitMtl(null);
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
