import LoadingSpinner from "@/components/loading-spinner";
import SizePicker from "@/components/stepper/try-on/size-picker";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { usePreviewFiles, useTryOnForm } from "@/lib/hooks";
import useFitObjStore from "@/store/useFitObjStore";
import ClothingPicker from "./clothing-picker";

type ClothingType = "t-shirt" | "sweatshirt" | "hoodie" | "pants";

const clothingTypeMap: Record<ClothingType, "tops" | "bottoms"> = {
	"t-shirt": "tops",
	sweatshirt: "tops",
	hoodie: "tops",
	pants: "bottoms",
};

const TryOnStep = () => {
	const { previewFiles, loading } = usePreviewFiles();
	const { form, onSubmit } = useTryOnForm();
	const { isFitObjLoading } = useFitObjStore();

	const categories = [
		{
			type: "tops",
			items: previewFiles.filter(
				(file) => clothingTypeMap[file.name as ClothingType] === "tops"
			),
		},
		{
			type: "bottoms",
			items: previewFiles.filter(
				(file) => clothingTypeMap[file.name as ClothingType] === "bottoms"
			),
		},
	];

	if (loading) {
		return (
			<Card className="flex justify-center items-center h-full">
				<CardContent>
					<LoadingSpinner />
				</CardContent>
			</Card>
		);
	}

	return (
		<Form {...form}>
			<form
				onSubmit={form.handleSubmit(onSubmit)}
				className="flex flex-col gap-4 h-full"
			>
				<Card className="flex flex-col justify-center items-center h-full">
					<CardContent className="py-4 w-full h-full">
						<ClothingPicker form={form} categories={categories} />
					</CardContent>
					<CardFooter className="flex flex-col justify-center items-center gap-6">
						<SizePicker form={form} disabled={isFitObjLoading} />
						<div className="flex justify-center items-center w-full">
							<Button
								size={"lg"}
								variant={isFitObjLoading ? "secondary" : "default"}
								disabled={isFitObjLoading}
								className="disabled:opacity-100"
							>
								{isFitObjLoading ? <LoadingSpinner /> : <span>Try on</span>}
							</Button>
						</div>
					</CardFooter>
				</Card>
			</form>
		</Form>
	);
};

export default TryOnStep;
