import {
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";
import {
	HoverCard,
	HoverCardContent,
	HoverCardTrigger,
} from "@/components/ui/hover-card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { tryonSchema } from "@/schemas";
import { Info } from "lucide-react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface QualityPickerProps {
	form: UseFormReturn<z.infer<typeof tryonSchema>>;
	disabled?: boolean;
}

const QualityPicker = ({ form, disabled }: QualityPickerProps) => {
	return (
		<div className="flex justify-center items-center gap-4 -mt-4">
			<FormField
				control={form.control}
				name="quality"
				render={({ field }) => (
					<FormItem>
						<HoverCard>
							<HoverCardTrigger className="flex items-center gap-2">
								<FormLabel className="hover:underline">Quality</FormLabel>
								<Info className="w-4 h-4 text-primary hover:text-primary/60" />
							</HoverCardTrigger>
							<HoverCardContent>
								<p>
									The higher the quality, the more detailed the cloth simulation
									will be. This also affects the simulation time.
								</p>
							</HoverCardContent>
						</HoverCard>
						<Select
							onValueChange={(value: string) => field.onChange(Number(value))}
							defaultValue={field.value.toString()}
							disabled={disabled}
						>
							<FormControl>
								<SelectTrigger>
									<SelectValue placeholder="Quality" />
								</SelectTrigger>
							</FormControl>
							<SelectContent>
								<SelectItem value="1">1</SelectItem>
								<SelectItem value="2">2</SelectItem>
								<SelectItem value="3">3</SelectItem>
								<SelectItem value="4">4</SelectItem>
								<SelectItem value="5">5</SelectItem>
								<SelectItem value="6">6</SelectItem>
								<SelectItem value="7">7</SelectItem>
								<SelectItem value="8">8</SelectItem>
								<SelectItem value="9">9</SelectItem>
								<SelectItem value="10">10</SelectItem>
							</SelectContent>
						</Select>
						<FormMessage />
					</FormItem>
				)}
			/>
		</div>
	);
};

export default QualityPicker;
