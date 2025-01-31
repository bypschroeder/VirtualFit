import { handleReset } from "@/lib/handlers";
import useFitObjStore from "@/store/useFitObjStore";
import useGenerationStore from "@/store/useGenerationStore";
import useImageStore from "@/store/useImageStore";
import useObjStore from "@/store/useObjStore";
import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
	AlertDialogTrigger,
} from "../ui/alert-dialog";
import { Button } from "../ui/button";

interface StepNavProps {
	stepper: {
		isFirst: boolean;
		isLast: boolean;
		prev: () => void;
		next: () => void;
	};
}

const StepNav = ({ stepper }: StepNavProps) => {
	const { obj, setObj } = useObjStore();
	const { setFitObj, isFitObjLoading } = useFitObjStore();
	const { setImage } = useImageStore();
	const { isGenerating } = useGenerationStore();

	const loading = obj === null || isGenerating || isFitObjLoading;

	return (
		<div className="flex justify-between items-center mt-4">
			<Button
				size={"lg"}
				className="w-40"
				variant={"secondary"}
				disabled={stepper.isFirst || loading}
				onClick={stepper.prev}
			>
				Previous
			</Button>
			{!stepper.isLast ? (
				<Button
					size={"lg"}
					className="w-40"
					onClick={stepper.next}
					disabled={!obj || loading}
				>
					Next
				</Button>
			) : (
				<AlertDialog>
					<AlertDialogTrigger asChild>
						<Button
							size={"lg"}
							className="w-40"
							variant={"destructive"}
							disabled={loading}
							type="reset"
						>
							Reset
						</Button>
					</AlertDialogTrigger>
					<AlertDialogContent>
						<AlertDialogHeader>
							<AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
							<AlertDialogDescription>
								This action cannot be undone. All generated models will be lost.
							</AlertDialogDescription>
						</AlertDialogHeader>
						<AlertDialogFooter>
							<AlertDialogCancel>Cancel</AlertDialogCancel>
							<AlertDialogAction
								className="bg-destructive hover:bg-destructive/90 text-destructive-foreground"
								onClick={() => handleReset(setObj, setFitObj, setImage)}
							>
								Reset
							</AlertDialogAction>
						</AlertDialogFooter>
					</AlertDialogContent>
				</AlertDialog>
			)}
		</div>
	);
};

export default StepNav;
