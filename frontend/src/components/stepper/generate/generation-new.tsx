import { Button } from "@/components/ui/button";
import { Box, RotateCcw, TriangleAlert } from "lucide-react";

interface GenerationNewProps {
	error: string | null;
	handleResetImage: () => void;
}

const GenerationNew = ({ error, handleResetImage }: GenerationNewProps) => {
	return (
		<div className="flex flex-col items-center gap-4">
			<div className="flex items-center gap-4 h-10">
				<Button variant={"destructive"} onClick={handleResetImage} type="reset">
					<RotateCcw />
					<span>Reset Image</span>
				</Button>
				<Button type="submit">
					<Box />
					<span>Generate Model</span>
				</Button>
			</div>
			{error && (
				<div className="flex justify-center items-center gap-2">
					<TriangleAlert className="w-5 h-5 text-destructive" />
					<span className="font-semibold text-destructive text-sm">
						{error}
					</span>
				</div>
			)}
		</div>
	);
};

export default GenerationNew;
