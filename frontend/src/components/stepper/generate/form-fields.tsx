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
import { useEffect, useState } from "react";
import { UseFormReturn } from "react-hook-form";
import { z } from "zod";

interface FormFieldsProps {
	form: UseFormReturn<z.infer<typeof generateSchema>>;
}

const FormFields = ({ form }: FormFieldsProps) => {
	const { isGenerating, generatingDone } = useGenerationStore();

	const [selectValue, setSelectValue] = useState<"male" | "female">(
		form.getValues("gender")
	);

	// FIXME: Select doesnt reset when not going next
	useEffect(() => {
		setSelectValue(form.getValues("gender"));
	}, [form, form.getValues("gender")]);
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
							disabled={generatingDone || isGenerating}
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
								placeholder="Height"
								{...field}
								type="number"
								value={field.value === 0 ? "" : field.value}
								disabled={generatingDone || isGenerating}
							/>
						</FormControl>
						<FormMessage />
					</FormItem>
				)}
			/>
			<FormField
				control={form.control}
				name="weight"
				render={({ field }) => (
					<FormItem className="w-full">
						<FormLabel>Weight</FormLabel>
						<FormControl>
							<Input
								placeholder="Weight"
								{...field}
								type="number"
								value={field.value === 0 ? "" : field.value}
								disabled={generatingDone || isGenerating}
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
