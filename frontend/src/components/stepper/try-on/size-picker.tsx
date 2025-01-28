import { FormControl, FormField, FormItem } from "@/components/ui/form";
import { tryonSchema } from "@/schemas";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";
import { Button } from "../../ui/button";

interface SizePickerProps {
	form: UseFormReturn<z.infer<typeof tryonSchema>>;
	disabled?: boolean;
}

const SizePicker = ({ form, disabled }: SizePickerProps) => {
	const sizes = ["XS", "S", "M", "L", "XL", "XXL"];

	return (
		<FormField
			control={form.control}
			name="size"
			render={({ field }) => (
				<FormItem>
					<FormControl>
						<div className="flex items-center">
							{sizes.map((size) => (
								<Button
									variant={field.value === size ? "default" : "outline"}
									className="rounded-none w-10"
									key={size}
									onClick={() => field.onChange(size)}
									type="button"
									disabled={disabled}
								>
									{size}
								</Button>
							))}
						</div>
					</FormControl>
				</FormItem>
			)}
		/>
	);
};

export default SizePicker;
