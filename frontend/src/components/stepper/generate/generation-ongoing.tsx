import LoadingSpinner from "@/components/loading-spinner";
import {
	HoverCard,
	HoverCardContent,
	HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Info } from "lucide-react";

const GenerationOngoing = () => {
	return (
		<div className="flex justify-center items-center gap-4 h-10">
			<LoadingSpinner className="w-8 h-8" />
			<span className="font-semibold text-lg">Generating Model...</span>
			<HoverCard>
				<HoverCardTrigger>
					<Info className="w-6 h-6 text-primary hover:text-primary/60" />
				</HoverCardTrigger>
				<HoverCardContent>
					The generation usually takes around 1-2 minutes. Be patient.
				</HoverCardContent>
			</HoverCard>
		</div>
	);
};

export default GenerationOngoing;
