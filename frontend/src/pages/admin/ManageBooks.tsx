import { useState } from 'react';
import { Plus, Pencil, Trash2, Search, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { useBooks, useCreateBook, useUpdateBook, useDeleteBook } from '@/hooks/useBooks';
import { StarRating } from '@/components/common/StarRating';
import { BOOK_CATEGORIES, type Book, type CreateBookRequest } from '@/types/book.types';

interface BookFormFieldsProps {
  formData: Partial<CreateBookRequest>;
  setFormData: (data: Partial<CreateBookRequest>) => void;
}

const BookFormFields = ({ formData, setFormData }: BookFormFieldsProps) => (
  <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="isbn">ISBN *</Label>
        <Input
          id="isbn"
          value={formData.isbn || ''}
          onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
          placeholder="978-0-123456-78-9"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="title">Title *</Label>
        <Input
          id="title"
          value={formData.title || ''}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Book Title"
        />
      </div>
    </div>

    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="author">Author *</Label>
        <Input
          id="author"
          value={formData.author || ''}
          onChange={(e) => setFormData({ ...formData, author: e.target.value })}
          placeholder="Author Name"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="publisher">Publisher *</Label>
        <Input
          id="publisher"
          value={formData.publisher || ''}
          onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
          placeholder="Publisher Name"
        />
      </div>
    </div>

    <div className="grid grid-cols-3 gap-4">
      <div className="space-y-2">
        <Label htmlFor="publication_year">Year *</Label>
        <Input
          id="publication_year"
          type="number"
          value={formData.publication_year || ''}
          onChange={(e) => setFormData({ ...formData, publication_year: parseInt(e.target.value) })}
          placeholder="2024"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="pages">Pages *</Label>
        <Input
          id="pages"
          type="number"
          value={formData.pages || ''}
          onChange={(e) => setFormData({ ...formData, pages: parseInt(e.target.value) })}
          placeholder="300"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="category">Category *</Label>
        <Select
          value={formData.category}
          onValueChange={(value) => setFormData({ ...formData, category: value as any })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            {BOOK_CATEGORIES.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>

    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="language">Language</Label>
        <Input
          id="language"
          value={formData.language || ''}
          onChange={(e) => setFormData({ ...formData, language: e.target.value })}
          placeholder="Français"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="cover_image_url">Cover Image URL</Label>
        <Input
          id="cover_image_url"
          value={formData.cover_image_url || ''}
          onChange={(e) => setFormData({ ...formData, cover_image_url: e.target.value })}
          placeholder="https://..."
        />
      </div>
    </div>

    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="total_copies">Total Copies</Label>
        <Input
          id="total_copies"
          type="number"
          value={formData.total_copies || ''}
          onChange={(e) => setFormData({ ...formData, total_copies: parseInt(e.target.value) })}
          placeholder="5"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="available_copies">Available Copies</Label>
        <Input
          id="available_copies"
          type="number"
          value={formData.available_copies || ''}
          onChange={(e) => setFormData({ ...formData, available_copies: parseInt(e.target.value) })}
          placeholder="5"
        />
      </div>
    </div>

    <div className="space-y-2">
      <Label htmlFor="description">Description</Label>
      <Textarea
        id="description"
        value={formData.description || ''}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        placeholder="Book description..."
        rows={3}
      />
    </div>
  </div>
);

const ManageBooks = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [formData, setFormData] = useState<Partial<CreateBookRequest>>({});

  const { data: booksData, isLoading } = useBooks({ page: 1, page_size: 50 });
  const createBook = useCreateBook();
  const updateBook = useUpdateBook();
  const deleteBook = useDeleteBook();

  const books = booksData?.results || [];
  const filteredBooks = books.filter(book =>
    book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    book.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
    book.isbn.includes(searchQuery)
  );

  const resetForm = () => {
    setFormData({});
    setSelectedBook(null);
  };

  const handleAddBook = () => {
    resetForm();
    setIsAddModalOpen(true);
  };

  const handleEditBook = (book: Book) => {
    setSelectedBook(book);
    setFormData({
      isbn: book.isbn,
      title: book.title,
      author: book.author,
      publisher: book.publisher,
      publication_year: book.publication_year,
      category: book.category,
      description: book.description,
      cover_image_url: book.cover_image_url,
      language: book.language,
      pages: book.pages,
      total_copies: book.total_copies,
      available_copies: book.available_copies,
    });
    setIsEditModalOpen(true);
  };

  const handleDeleteBook = (book: Book) => {
    setSelectedBook(book);
    setIsDeleteDialogOpen(true);
  };

  const handleSubmitAdd = async () => {
    try {
      await createBook.mutateAsync(formData as CreateBookRequest);
      toast({ title: "Creation Queued", description: "Book creation request has been sent." });
      setIsAddModalOpen(false);
      resetForm();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to add book",
        variant: "destructive",
      });
    }
  };

  const handleSubmitEdit = async () => {
    if (!selectedBook) return;
    try {
      await updateBook.mutateAsync({ id: selectedBook.id, data: formData as CreateBookRequest });
      toast({ title: "Update Queued", description: "Book update request has been sent." });
      setIsEditModalOpen(false);
      resetForm();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to update book",
        variant: "destructive",
      });
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedBook) return;
    try {
      await deleteBook.mutateAsync(selectedBook.id);
      toast({ title: "Deletion Queued", description: "Book deletion request has been sent." });
      setIsDeleteDialogOpen(false);
      resetForm();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to delete book",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-foreground">Manage Books</h1>
          <p className="text-muted-foreground">Add, edit, and remove books from the catalog</p>
        </div>
        <Button onClick={handleAddBook} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Book
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search books by title, author, or ISBN..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Badge variant="secondary">{filteredBooks.length} books</Badge>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">Cover</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Author</TableHead>
              <TableHead>ISBN</TableHead>
              <TableHead>Category</TableHead>
              <TableHead className="text-center">Copies</TableHead>
              <TableHead className="text-center">Rating</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8">
                  Loading books...
                </TableCell>
              </TableRow>
            ) : filteredBooks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8">
                  <BookOpen className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">No books found</p>
                </TableCell>
              </TableRow>
            ) : (
              filteredBooks.map((book) => (
                <TableRow key={book.id}>
                  <TableCell>
                    <div className="h-12 w-9 rounded bg-muted flex items-center justify-center overflow-hidden">
                      {book.cover_image_url ? (
                        <img
                          src={book.cover_image_url}
                          alt={book.title}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <BookOpen className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="font-medium max-w-[200px] truncate">
                    {book.title}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{book.author}</TableCell>
                  <TableCell className="font-mono text-xs">{book.isbn}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{book.category}</Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className={book.available_copies === 0 ? 'text-destructive' : 'text-foreground'}>
                      {book.available_copies}/{book.total_copies}
                    </span>
                  </TableCell>
                  <TableCell className="text-center">
                    <StarRating rating={parseFloat(book.average_rating)} size="sm" />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditBook(book)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteBook(book)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Add Book Modal */}
      <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add New Book</DialogTitle>
            <DialogDescription>
              Fill in the details to add a new book to the catalog.
            </DialogDescription>
          </DialogHeader>
          <BookFormFields formData={formData} setFormData={setFormData} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitAdd} disabled={createBook.isPending}>
              {createBook.isPending ? 'Adding...' : 'Add Book'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Book Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Book</DialogTitle>
            <DialogDescription>
              Update the book details.
            </DialogDescription>
          </DialogHeader>
          <BookFormFields formData={formData} setFormData={setFormData} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitEdit} disabled={updateBook.isPending}>
              {updateBook.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Book</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{selectedBook?.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteBook.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ManageBooks;
