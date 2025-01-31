import LoadingSpinner from "@/components/loading-spinner";
import {
	Card,
	CardContent,
	CardFooter,
	CardHeader,
} from "@/components/ui/card";

const GenerationOngoing = () => {
	return (
		<div className="z-10 absolute inset-0 flex justify-center items-center bg-black/75">
			<Card>
				<CardHeader>
					<h1 className="font-bold text-2xl text-center">Generation ongoing</h1>
				</CardHeader>
				<CardContent>
					<span className="text-center">
						This usually takes around 30 seconds.
					</span>
				</CardContent>
				<CardFooter>
					<div className="flex justify-center items-center w-full">
						<LoadingSpinner className="w-9 h-9" />
					</div>
				</CardFooter>
			</Card>
		</div>
	);
};

export default GenerationOngoing;
