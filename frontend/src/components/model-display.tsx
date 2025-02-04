import { handleDownload, handleReset } from "@/lib/handlers";
import useFitObjStore from "@/store/useFitObjStore";
import useImageStore from "@/store/useImageStore";
import useObjStore from "@/store/useObjStore";
import { Download, RotateCcw } from "lucide-react";
import LoadingSpinner from "./loading-spinner";
import ModelViewer from "./model-viewer";
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
} from "./ui/alert-dialog";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "./ui/hover-card";

const ModelDisplay = () => {
	// State Management
	const { obj, setObj, isObjLoading } = useObjStore();
	const { fitObj, fitMtl, setFitObj, setFitMtl, isFitObjLoading } =
		useFitObjStore();
	const { setImage } = useImageStore();
	const isLoading = isObjLoading || isFitObjLoading;

	return (
		<Card className="relative col-span-2 select-none">
			{!isLoading && (fitObj || obj) && (
				<div className="top-0 right-0 z-10 absolute flex gap-4 p-4">
					<AlertDialog>
						<HoverCard>
							<HoverCardTrigger>
								<AlertDialogTrigger asChild>
									<Button size={"icon"} variant={"destructive"}>
										<RotateCcw />
									</Button>
								</AlertDialogTrigger>
							</HoverCardTrigger>
							<HoverCardContent className="w-auto">Reset</HoverCardContent>
						</HoverCard>
						<AlertDialogContent>
							<AlertDialogHeader>
								<AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
								<AlertDialogDescription>
									This action cannot be undone. All generated models will be
									lost.
								</AlertDialogDescription>
							</AlertDialogHeader>
							<AlertDialogFooter>
								<AlertDialogCancel>Cancel</AlertDialogCancel>
								<AlertDialogAction
									className="bg-destructive hover:bg-destructive/90 text-destructive-foreground"
									onClick={() =>
										handleReset(setObj, setFitObj, setFitMtl, setImage)
									}
								>
									Reset
								</AlertDialogAction>
							</AlertDialogFooter>
						</AlertDialogContent>
					</AlertDialog>
					<HoverCard>
						<HoverCardTrigger>
							<Button
								size={"icon"}
								onClick={() => handleDownload(fitObj || obj, fitMtl, !!fitObj)}
							>
								<Download />
							</Button>
						</HoverCardTrigger>
						<HoverCardContent className="w-auto">Download</HoverCardContent>
					</HoverCard>
				</div>
			)}
			{isLoading ? (
				<div className="flex justify-center items-center w-full h-full">
					<LoadingSpinner />
				</div>
			) : fitObj ? (
				<ModelViewer obj={fitObj} mtl={fitMtl} />
			) : obj ? (
				<ModelViewer obj={obj} />
			) : (
				<span className="flex justify-center items-center w-full h-full text-center">
					No model generated yet. <br />
					Please generate a 3D model first.
				</span>
			)}
		</Card>
	);
};

export default ModelDisplay;
