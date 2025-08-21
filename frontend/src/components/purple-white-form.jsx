"use client";
import { ChevronLeft, LucideArrowDownNarrowWide, RefreshCcw, RotateCcw } from 'lucide-react';
import Link from 'next/link';
import React from 'react';
import { toast } from 'sonner';


const PurpleWhiteForm = ({ formData }) => {
  const [formValues, setFormValues] = React.useState({});

  const handleChange = (fieldId, value) => {
    setFormValues((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form submitted:', formValues);
  
    // Transform formValues into the expected array format with proper typing
    const responses = Object.entries(formValues).map(([field_id, answer]) => ({
      field_id,
      answer,
    }));
  
    const submission = {
      form_id: formData.form_id,
      responses
    };
  
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/submit/${formData.form_id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(submission),
        }
      );
  
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit form');
      }

      // confirm with user
      const confirm = window.confirm('Form submitted successfully! Do you want to download the PDF?');
      if (!confirm) {
        return;
      }

      // Handle PDF response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `filled_form_${formData.form_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
      toast.success('Form submitted and PDF downloaded successfully!');
    } catch (error) {
      console.error('Error submitting form:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to submit form');
    }
  };
  

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white to-purple-50 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-4xl p-8 space-y-6 bg-white rounded-xl shadow-lg border border-purple-100"
      >
        <Link href="/dashboard"><ChevronLeft className="w-6 h-6"/></Link>
        <h2 className="text-2xl font-bold text-center text-gray-800">
          Form
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {formData.questions.map((question) => (
            <div key={question.field_id} className="space-y-2">
              <label
                htmlFor={question.field_id}
                className="block text-sm font-medium text-gray-700"
              >
                {question.field_name}
              </label>
              <input
                type="text"
                id={question.field_id}
                value={formValues[question.field_id] || ''}
                onChange={(e) => handleChange(question.field_id, e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition duration-200"
                placeholder={question.question}
              />
            </div>
          ))}
        </div>
        <div className="flex gap-2 items-center">
          <button
            type="submit"
            className="w-full md:w-auto md:px-12 py-3 bg-gradient-to-br from-purple-600 to-blue-700 text-white font-medium rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition duration-200"
          >
            Submit
          </button>
          <Link href="/dashboard"><RotateCcw className="w-6 h-6"/></Link>
        </div>
        
      </form>
    </div>
  );
};

export default PurpleWhiteForm;