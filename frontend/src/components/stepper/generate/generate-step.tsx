import { Button } from "@/components/ui/button";
import { handleResetImage } from "@/lib/handlers";
import { useGenerateForm } from "@/lib/hooks";
import useErrorStore from "@/store/useErrorStore";
import useFitObjStore from "@/store/useFitObjStore";
import useGenerationStore from "@/store/useGenerationStore";
import useImageStore from "@/store/useImageStore";
import useObjStore from "@/store/useObjStore";
import { Box, Trash2, TriangleAlert } from "lucide-react";
import { Card, CardContent } from "../../ui/card";
import { Form } from "../../ui/form";
import FormFields from "./form-fields";
import GenerationOngoing from "./generation-ongoing";
import ImageCapture from "./image-capture";
import ImageUploader from "./image-uploader";

const GenerateStep = () => {
	// State Management
	const { image, setImage } = useImageStore();
	const { isGenerating } = useGenerationStore();
	const { obj, setObj } = useObjStore();
	const { setFitObj } = useFitObjStore();
	const { generationError, setGenerationError } = useErrorStore();

	const { form, onSubmit } = useGenerateForm();

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
								<div className="relative rounded-md max-w-4xl max-h-[36rem] overflow-hidden">
									<div className="top-0 left-0 z-10 absolute p-2">
										<Button
											variant={"destructive"}
											size={"icon"}
											type="button"
											onClick={() =>
												handleResetImage(
													setObj,
													setFitObj,
													setImage,
													setGenerationError
												)
											}
											disabled={isGenerating && !obj}
										>
											<Trash2 />
										</Button>
									</div>
									<img
										src={image}
										alt="Uploaded Image"
										className="w-full h-full object-contain"
									/>
									{!obj && !isGenerating && (
										<div className="bottom-0 z-10 absolute flex flex-col items-center gap-4 mb-4 w-full">
											<Button type="submit">
												<Box />
												<span>Generate Model</span>
											</Button>
											{generationError && (
												<div className="flex justify-center items-center gap-2 bg-background p-2 border border-border rounded-md">
													<TriangleAlert className="w-5 h-5 text-destructive" />
													<span className="font-semibold text-destructive text-sm">
														{generationError}
													</span>
												</div>
											)}
										</div>
									)}
								</div>
								{isGenerating && !obj && <GenerationOngoing />}
							</div>
						)}
					</CardContent>
				</Card>
			</form>
		</Form>
	);
};

export default GenerateStep;
