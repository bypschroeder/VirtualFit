import useObjStore from "@/store/useObjStore";
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
	const obj = useObjStore((state) => state.obj);
	return (
		<div className="flex justify-between items-center mt-4">
			<Button
				size={"lg"}
				className="w-40"
				variant={"secondary"}
				disabled={stepper.isFirst}
				onClick={stepper.prev}
			>
				Previous
			</Button>
			{!stepper.isLast ? (
				<Button
					size={"lg"}
					className="w-40"
					onClick={stepper.next}
					disabled={!obj}
				>
					Next
				</Button>
			) : (
				<Button size={"lg"} className="w-40" variant={"destructive"}>
					Reset
				</Button>
			)}
		</div>
	);
};

export default StepNav;
