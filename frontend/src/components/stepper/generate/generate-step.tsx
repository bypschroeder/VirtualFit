import { generateSchema } from "@/schemas";
import useFormStore from "@/store/useFormStore";
import useGenerationStore from "@/store/useGenerationStore";
import useImageStore from "@/store/useImageStore";
import useObjStore from "@/store/useObjStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Card, CardContent } from "../../ui/card";
import { Form } from "../../ui/form";
import FormFields from "./form-fields";
import GenerationDone from "./generation-done";
import GenerationNew from "./generation-new";
import GenerationOngoing from "./generation-ongoing";
import ImageCapture from "./image-capture";
import ImageUploader from "./image-uploader";

const GenerateStep = () => {
	const [error, setError] = useState<string | null>(null);

	const { image, setImage } = useImageStore();
	const { isGenerating, setIsGenerating, generatingDone, setGeneratingDone } =
		useGenerationStore();
	const { gender, setGender, height, setHeight, weight, setWeight } =
		useFormStore();
	const { setObj } = useObjStore();

	const form = useForm<z.infer<typeof generateSchema>>({
		resolver: zodResolver(generateSchema),
		defaultValues: {
			gender: gender,
			weight: weight,
			height: height,
			image: "",
		},
	});

	const onSubmit = async (values: z.infer<typeof generateSchema>) => {
		try {
			setError(null);

			setGender(values.gender);
			setWeight(values.weight);
			setHeight(values.height);

			const formData = new FormData();
			formData.append("image", values.image);
			formData.append("gender", values.gender);
			// formData.append("height", String(values.height));
			// formData.append("weight", String(values.weight));
			setIsGenerating(true);
			const response = await fetch("http://localhost:3000/generate-3d-model", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				throw new Error(`Error: ${response.status} - ${response.statusText}`);
			}

			const obj = await response.text();

			setObj(obj);
			setGeneratingDone(true);
			setIsGenerating(false);
		} catch (error) {
			console.error("Error generating 3D model: ", error);
			setIsGenerating(false);
			setGeneratingDone(false);
			setError("Error generating 3D model. Please try again.");
		}
	};

	const handleResetImage = () => {
		setImage(null);
		setError(null);
	};

	return (
		<Form {...form}>
			<form
				onSubmit={form.handleSubmit(onSubmit)}
				className="flex flex-col gap-4 h-full"
			>
				<FormFields form={form} />
				<Card className="flex justify-center items-center h-full">
					<CardContent className="flex flex-col items-center gap-4 pt-6 w-full h-full">
						{!image ? (
							<div className="flex flex-col justify-center items-center gap-4 h-full">
								<h2 className="font-semibold text-lg">Add an image</h2>
								<div className="flex justify-center items-center gap-4">
									<ImageUploader form={form} />
									<ImageCapture form={form} />
								</div>
							</div>
						) : (
							<div className="flex flex-col justify-center items-center gap-4 w-full h-full">
								<div className="relative rounded-md max-w-4xl max-h-[32rem] overflow-hidden">
									<img
										src={image}
										alt="Uploaded Image"
										className="w-full h-full object-contain"
									/>
								</div>
								{!generatingDone && !isGenerating && (
									<GenerationNew
										error={error}
										handleResetImage={handleResetImage}
									/>
								)}
								{isGenerating && !generatingDone && <GenerationOngoing />}
								{!isGenerating && generatingDone && (
									<GenerationDone form={form} />
								)}
							</div>
						)}
					</CardContent>
				</Card>
			</form>
		</Form>
	);
};

export default GenerateStep;
