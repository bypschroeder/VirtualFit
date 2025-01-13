import { Button } from "@/components/ui/button";
import { generateSchema } from "@/schemas";
import useFormStore from "@/store/useFormStore";
import useGenerationStore from "@/store/useGenerationStore";
import useImageStore from "@/store/useImageStore";
import useObjStore from "@/store/useObjStore";
import { Download, RotateCcw } from "lucide-react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface GenerationDoneProps {
	form: UseFormReturn<z.infer<typeof generateSchema>>;
}

const GenerationDone = ({ form }: GenerationDoneProps) => {
	const { obj, setObj } = useObjStore();
	const { setIsGenerating, setGeneratingDone } = useGenerationStore();
	const { setGender, setHeight, setWeight } = useFormStore();
	const { setImage } = useImageStore();

	const handleResetModel = () => {
		setObj(null);
		setIsGenerating(false);
		setGeneratingDone(false);
		setGender(undefined);
		setHeight(0);
		setWeight(0);
		form.setValue("gender", undefined!);
		form.setValue("height", 0);
		form.setValue("weight", 0);
		form.setValue("image", "");
		setImage(null);
	};

	const handleDownloadModel = () => {
		const blob = new Blob([obj as string], {
			type: "text/plain;charset=utf-8",
		});
		const url = URL.createObjectURL(blob);

		const a = document.createElement("a");
		a.href = url;
		a.download = "model.obj";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(url);
	};

	return (
		<div className="flex items-center gap-4 h-10">
			<Button variant={"destructive"} onClick={handleResetModel} type="reset">
				<RotateCcw />
				<span>Reset Model</span>
			</Button>
			<Button onClick={handleDownloadModel} type="button">
				<Download />
				<span>Download Model</span>
			</Button>
		</div>
	);
};

export default GenerationDone;
