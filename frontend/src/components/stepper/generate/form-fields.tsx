import {
	FormControl,
	FormField,
	FormItem,
	FormLabel,
	FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { generateSchema } from "@/schemas";
import useGenerationStore from "@/store/useGenerationStore";
import useObjStore from "@/store/useObjStore";
import { useState } from "react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface FormFieldsProps {
	form: UseFormReturn<z.infer<typeof generateSchema>>;
}

const FormFields = ({ form }: FormFieldsProps) => {
	// State Management
	const { isGenerating } = useGenerationStore();
	const { obj } = useObjStore();

	// Form
	const [selectValue, setSelectValue] = useState<"male" | "female">(
		form.getValues("gender")
	);

	return (
		<div className="flex justify-evenly gap-12">
			<FormField
				control={form.control}
				name="gender"
				render={({ field }) => (
					<FormItem className="w-full">
						<FormLabel>Gender</FormLabel>
						<Select
							onValueChange={(value: "male" | "female") => {
								field.onChange(value);
								setSelectValue(value);
							}}
							disabled={!!obj || isGenerating}
							value={selectValue}
						>
							<FormControl>
								<SelectTrigger>
									<SelectValue placeholder="Select a gender" />
								</SelectTrigger>
							</FormControl>
							<SelectContent>
								<SelectItem value="male">Male</SelectItem>
								<SelectItem value="female">Female</SelectItem>
							</SelectContent>
						</Select>
						<FormMessage />
					</FormItem>
				)}
			/>
			<FormField
				control={form.control}
				name="height"
				render={({ field }) => (
					<FormItem className="w-full">
						<FormLabel>Height</FormLabel>
						<FormControl>
							<Input
								placeholder="e.g 1.75"
								{...field}
								type="number"
								value={field.value === 0 ? "" : field.value}
								disabled={!!obj || isGenerating}
								step={0.01}
							/>
						</FormControl>
						<FormMessage />
					</FormItem>
				)}
			/>
		</div>
	);
};

export default FormFields;
