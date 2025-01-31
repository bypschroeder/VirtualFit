import { Button } from "@/components/ui/button";
import { Box, TriangleAlert } from "lucide-react";

interface GenerationNewProps {
	error: string | null;
}

const GenerationNew = ({ error }: GenerationNewProps) => {
	return (
		<div className="right-0 bottom-0 left-0 absolute flex flex-col items-center gap-4 mb-4 w-full">
			<Button type="submit">
				<Box />
				<span>Generate Model</span>
			</Button>
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
