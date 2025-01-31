import { generateSchema, tryonSchema } from "@/schemas";
import useErrorStore from "@/store/useErrorStore";
import useFitObjStore from "@/store/useFitObjStore";
import useFormStore from "@/store/useFormStore";
import useGenerationStore from "@/store/useGenerationStore";
import useObjStore from "@/store/useObjStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

export const useGenerateForm = () => {
	const { gender, setGender, height, setHeight } = useFormStore();
	const { setObj, setIsObjLoading } = useObjStore();
	const { setFitObj } = useFitObjStore();
	const { setIsGenerating } = useGenerationStore();
	const { setGenerationError } = useErrorStore();

	const form = useForm<z.infer<typeof generateSchema>>({
		resolver: zodResolver(generateSchema),
		defaultValues: {
			gender: gender,
			height: height,
			image: "",
		},
	});

	const onSubmit = async (values: z.infer<typeof generateSchema>) => {
		try {
			setObj(null);
			setFitObj(null);
			setGenerationError(null);

			setGender(values.gender);
			setHeight(values.height);

			const formData = new FormData();
			formData.append("image", values.image);
			formData.append("gender", values.gender);
			formData.append("height", String(values.height));
			setIsGenerating(true);
			setIsObjLoading(true);
			const response = await fetch("http://api.localhost/generate-3d-model", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				throw new Error(`Error: ${response.status} - ${response.statusText}`);
			}

			const obj = await response.text();

			setObj(obj);
			setIsGenerating(false);
			setIsObjLoading(false);
		} catch (error) {
			console.error("Error generating 3D model: ", error);
			setIsGenerating(false);
			setIsObjLoading(false);
			setGenerationError("Error generating 3D model. Please try again.");
		}
	};

	return { form, onSubmit };
};

interface PreviewFile {
	name: string;
	path: string;
}

export const usePreviewFiles = () => {
	const [previewFiles, setPreviewFiles] = useState<PreviewFile[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const { gender } = useFormStore();
	const { setPreviewError } = useErrorStore();

	useEffect(() => {
		const fetchPreviews = async () => {
			try {
				const formData = new FormData();
				if (gender) {
					formData.append("gender", gender);
				} else {
					setPreviewError("Gender is undefined");
					console.error("Gender is undefined");
					return;
				}

				const response = await fetch("http://api.localhost/generate-previews", {
					method: "POST",
					body: formData,
				});

				if (!response.ok) {
					throw new Error(`Error: ${response.status} - ${response.statusText}`);
				}

				const data = await response.json();
				const presignedUrls = data.presigned_urls;

				const downloadedFiles = [];

				for (const index in presignedUrls) {
					const url = presignedUrls[index];
					const fileResponse = await fetch(url, {
						method: "GET",
					});

					if (!fileResponse.ok) {
						throw new Error(
							`Error: ${fileResponse.status} - ${fileResponse.statusText}`
						);
					}

					const blob = await fileResponse.blob();
					const objectUrl = URL.createObjectURL(blob);
					const parts = url.split("/");
					downloadedFiles.push({
						name: parts[parts.length - 2],
						path: objectUrl,
					});
				}
				setPreviewFiles(downloadedFiles);
				setLoading(false);
			} catch (error) {
				setPreviewError("Error fetching previews. Please try again.");
				setLoading(false);
				console.error("Error fetching previews: ", error);
			}
		};
		fetchPreviews();
	}, [gender, setPreviewError]);

	return { previewFiles, loading };
};

export const useTryOnForm = () => {
	const { obj } = useObjStore();
	const { setFitObj, setIsFitObjLoading } = useFitObjStore();
	const { setTryOnError } = useErrorStore();

	const form = useForm<z.infer<typeof tryonSchema>>({
		resolver: zodResolver(tryonSchema),
		defaultValues: {
			obj: undefined,
			garment: undefined,
			gender: undefined,
			size: "M",
		},
	});

	useEffect(() => {
		if (obj) {
			const objBlob = new Blob([obj], { type: "application/octet-stream" });
			const objFile = new File([objBlob], "model.obj", {
				type: "application/octet-stream",
			});

			form.setValue("obj", objFile);
		}
	}, [obj, form]);

	const onSubmit = async (values: z.infer<typeof tryonSchema>) => {
		setFitObj(null);
		setIsFitObjLoading(true);

		try {
			const formData = new FormData();
			formData.append("obj", values.obj);
			formData.append("garment", values.garment);
			formData.append("gender", values.gender);
			formData.append("size", values.size);

			const response = await fetch("http://api.localhost/try-on", {
				method: "POST",
				body: formData,
			});

			if (!response.ok)
				throw new Error(`Error: ${response.status} - ${response.statusText}`);

			setFitObj(await response.text());
		} catch (error) {
			setTryOnError("Error generating the virtual fit. Please try again.");
			console.error("Error generating the virtual fit", error);
		} finally {
			setIsFitObjLoading(false);
		}
	};

	return { form, onSubmit };
};
